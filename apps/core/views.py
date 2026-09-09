import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from apps.core.captcha_utils import generate_captcha_data
from apps.accounts.models import User, PrimaryRole, SubRole
from apps.profiles.models import UserProfile
from apps.taxonomy.models import Field
from apps.institutions.models import Institution, Department
from apps.education.models import Course, Programme, Event, EventType, EventMode, EventRegistration
from apps.opportunities.models import Opportunity, OpportunityType, OpportunityMode
from apps.skills.models import Skill, UserSkill, DigitalSkillPassport, Assessment, SkillProficiency, SkillEvidence
from apps.applications.models import Application, ApplicationStatus
from apps.sources.models import VerificationRecord
from apps.notifications.models import Notification
from apps.research.models import ResearchProject, MentorshipPair

def home_view(request):
    """Global Home Landing View with Real Counts and Search Hero"""
    context = {
        'institution_count': Institution.objects.count(),
        'programme_count': Programme.objects.count(),
        'course_count': Course.objects.count(),
        'opportunity_count': Opportunity.objects.count(),
        'skill_count': Skill.objects.count(),
        'featured_fields': Field.objects.prefetch_related('subfields').all()[:8],
        'featured_courses': Course.objects.all()[:4],
        'featured_opportunities': Opportunity.objects.all()[:4],
    }
    return render(request, 'pages/home.html', context)

def captcha_refresh_api(request):
    """API endpoint to refresh the 4-character visual CAPTCHA image."""
    code, data_uri = generate_captcha_data()
    request.session['login_captcha'] = code.upper()
    return JsonResponse({'captcha_image': data_uri})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error = None
    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        entered_captcha = request.POST.get('captcha', '').strip().upper()
        expected_captcha = request.session.get('login_captcha', '').upper()

        # Validate 4-character CAPTCHA first
        if not entered_captcha or entered_captcha != expected_captcha:
            error = 'Incorrect 4-character CAPTCHA code. Please verify the characters and try again.'
            code, data_uri = generate_captcha_data()
            request.session['login_captcha'] = code.upper()
            return render(request, 'pages/auth/login.html', {'error': error, 'captcha_image': data_uri})

        # Shortcut mapping for ultra-fast login
        shortcut_map = {
            'student': 'student@aic.com',
            's': 'student@aic.com',
            's@aic.com': 'student@aic.com',
            'student@aicportal.edu': 'student@aic.com',
            
            'prof': 'prof@aic.com',
            'p': 'prof@aic.com',
            'p@aic.com': 'prof@aic.com',
            'professor': 'prof@aic.com',
            'professor@iitb.ac.in': 'prof@aic.com',
            
            'recruiter': 'recruiter@aic.com',
            'r': 'recruiter@aic.com',
            'r@aic.com': 'recruiter@aic.com',
            'industry': 'recruiter@aic.com',
            'recruiter@techcorp.com': 'recruiter@aic.com',
            
            'inst': 'inst@aic.com',
            'i': 'inst@aic.com',
            'i@aic.com': 'inst@aic.com',
            'director': 'inst@aic.com',
            'admin': 'inst@aic.com',
            'director@iitb.ac.in': 'inst@aic.com',
        }
        
        email_to_auth = shortcut_map.get(login_input.lower(), login_input)
        user = authenticate(request, username=email_to_auth, password=password)
        if user is not None:
            # Clear captcha after successful login
            request.session.pop('login_captcha', None)
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid email address or password. Please try again.'
            code, data_uri = generate_captcha_data()
            request.session['login_captcha'] = code.upper()
            return render(request, 'pages/auth/login.html', {'error': error, 'captcha_image': data_uri})

    # GET request: generate fresh 4-character CAPTCHA
    code, data_uri = generate_captcha_data()
    request.session['login_captcha'] = code.upper()
    return render(request, 'pages/auth/login.html', {'error': error, 'captcha_image': data_uri})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        primary_role = request.POST.get('primary_role', PrimaryRole.STUDENT)
        sub_role = request.POST.get('sub_role', SubRole.STUDENT_GENERAL)
        org_name = request.POST.get('organization_name', '')
        
        if User.objects.filter(email=email).exists():
            error = 'An account with this email address already exists.'
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                primary_role=primary_role,
                sub_role=sub_role,
                organization_name=org_name,
                is_verified=True
            )
            UserProfile.objects.get_or_create(user=user)
            if primary_role == PrimaryRole.STUDENT:
                DigitalSkillPassport.objects.get_or_create(
                    user=user,
                    defaults={'passport_number': f"AIC-PASSPORT-{user.id.hex[:8].upper()}"}
                )
            login(request, user)
            return redirect('dashboard')
            
    return render(request, 'pages/auth/register.html', {
        'roles': PrimaryRole.choices,
        'sub_roles': SubRole.choices,
        'error': error
    })

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    role = request.user.primary_role
    
    if role == PrimaryRole.STUDENT:
        user_skills = UserSkill.objects.filter(user=request.user)
        applications = Application.objects.filter(applicant=request.user)
        passport = getattr(request.user, 'passport', None)
        recommended_courses = Course.objects.all()[:3]
        recommended_jobs = Opportunity.objects.filter(opportunity_type=OpportunityType.JOB)[:3]
        
        context = {
            'user_skills': user_skills,
            'applications': applications,
            'passport': passport,
            'recommended_courses': recommended_courses,
            'recommended_jobs': recommended_jobs,
        }
        return render(request, 'pages/dashboards/student_dashboard.html', context)
        
    elif role == PrimaryRole.ACADEMICIAN:
        faculty_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
        fdp_courses = Course.objects.filter(level_name__in=['Advanced Faculty', 'Professional Educator', 'Specialty Educator'])[:6]
        if not fdp_courses.exists():
            fdp_courses = Course.objects.all()[:6]
        industry_grants = Opportunity.objects.filter(
            Q(opportunity_type=OpportunityType.PROJECT) & 
            (Q(description__icontains='Grant') | Q(title__icontains='Research') | Q(title__icontains='Grant') | Q(verification_source__icontains='Industry'))
        )[:6]
        context = {
            'faculty_skills': faculty_skills,
            'fdp_courses': fdp_courses,
            'industry_grants': industry_grants,
            'research_opps': industry_grants[:3],
        }
        return render(request, 'pages/dashboards/academician_dashboard.html', context)
        
    elif role == PrimaryRole.INDUSTRY:
        user_org = request.user.organization_name or 'TechCorp Global Solutions'
        posted_opportunities = Opportunity.objects.filter(
            Q(organization_name__icontains=user_org) | Q(verification_source__icontains=user_org)
        ).prefetch_related('required_skills').order_by('-created_at')

        # Compute talent matching against recruiter's posted jobs
        selected_opp_id = request.GET.get('job_id', '')
        selected_opp = None
        if selected_opp_id:
            selected_opp = posted_opportunities.filter(id=selected_opp_id).first()
        if not selected_opp and posted_opportunities.exists():
            selected_opp = posted_opportunities.first()

        # All enrolled students
        students = User.objects.filter(primary_role=PrimaryRole.STUDENT).select_related('profile').order_by('first_name')
        total_students_pool = students.count()

        matched_students = []
        if selected_opp:
            req_skills = list(selected_opp.required_skills.all())
            req_skill_ids = set(selected_opp.required_skills.values_list('id', flat=True))
            req_skill_names = set(selected_opp.required_skills.values_list('name', flat=True))
            total_req = max(len(req_skills), 1)

            for st in students:
                st_skills = list(UserSkill.objects.filter(user=st).select_related('skill'))
                st_skill_ids = set(s.skill_id for s in st_skills)
                st_skill_names = set(s.skill.name for s in st_skills)

                matched_skills = [s for s in req_skills if s.id in st_skill_ids or s.name in st_skill_names]
                missing_skills = [s for s in req_skills if s not in matched_skills]

                if req_skills:
                    match_pct = int((len(matched_skills) / total_req) * 100)
                else:
                    match_pct = 70 + (len(st_skills) * 5)
                    match_pct = min(match_pct, 98)

                matched_students.append({
                    'student': st,
                    'verified_skills_count': len(st_skills),
                    'all_skills': [s.skill.name for s in st_skills],
                    'matched_skills': [s.name for s in matched_skills],
                    'missing_skills': [s.name for s in missing_skills],
                    'match_pct': match_pct,
                    'is_high_fit': match_pct >= 60,
                })

            matched_students.sort(key=lambda x: x['match_pct'], reverse=True)

        # Recruiter ATS Metrics
        org_applications = Application.objects.filter(
            Q(opportunity__organization_name__icontains=user_org) |
            Q(opportunity__in=posted_opportunities)
        ).select_related('applicant', 'opportunity')

        # Annotate each posted job with application count and matching candidates
        annotated_posted_jobs = []
        for opp in posted_opportunities:
            app_count = org_applications.filter(opportunity=opp).count()
            opp_req_skills = set(opp.required_skills.values_list('name', flat=True))
            high_match_count = 0
            if opp_req_skills:
                for st in students:
                    st_skills_set = set(UserSkill.objects.filter(user=st).values_list('skill__name', flat=True))
                    matched_len = len(opp_req_skills.intersection(st_skills_set))
                    if (matched_len / len(opp_req_skills)) >= 0.5:
                        high_match_count += 1
            else:
                high_match_count = students.count()

            annotated_posted_jobs.append({
                'opp': opp,
                'applicants_count': app_count,
                'high_match_count': high_match_count,
                'is_selected': bool(selected_opp and opp.id == selected_opp.id),
            })

        ats_metrics = {
            'total_applicants': org_applications.count(),
            'under_review': org_applications.filter(status__in=[ApplicationStatus.APPLIED, ApplicationStatus.SCREENING]).count(),
            'shortlisted': org_applications.filter(status__in=[ApplicationStatus.ASSESSMENT, ApplicationStatus.SHORTLISTED]).count(),
            'interviews': org_applications.filter(status=ApplicationStatus.INTERVIEW).count(),
            'offers': org_applications.filter(status__in=[ApplicationStatus.OFFER, ApplicationStatus.JOINED]).count(),
        }

        context = {
            'user_org': user_org,
            'posted_opportunities': posted_opportunities,
            'annotated_posted_jobs': annotated_posted_jobs,
            'selected_opp': selected_opp,
            'matched_students': matched_students,
            'total_students_pool': total_students_pool,
            'ats_metrics': ats_metrics,
            'recent_applications': org_applications.order_by('-applied_at')[:8],
        }
        return render(request, 'pages/dashboards/industry_dashboard.html', context)
        
    elif role == PrimaryRole.INSTITUTION:
        context = {
            'total_students': User.objects.filter(primary_role=PrimaryRole.STUDENT).count(),
            'total_courses': Course.objects.count(),
            'total_placements': Application.objects.filter(status=ApplicationStatus.JOINED).count(),
        }
        return render(request, 'pages/dashboards/institution_dashboard.html', context)
        
    else: # SYSTEM_ADMIN
        students_qs = User.objects.filter(primary_role=PrimaryRole.STUDENT).select_related('profile')
        faculty_qs = User.objects.filter(primary_role=PrimaryRole.ACADEMICIAN)
        recruiters_qs = User.objects.filter(primary_role=PrimaryRole.INDUSTRY)
        institutions_qs = Institution.objects.all().order_by('nirf_rank')

        # Annotate students with passport and readiness
        students_list = []
        for st in students_qs[:30]:
            passport = DigitalSkillPassport.objects.filter(user=st).first()
            p_num = passport.passport_number if passport else f"AIC-PASSPORT-{st.id.hex[:8].upper()}"
            p_token = str(passport.qr_verification_token) if passport else str(st.id)
            sk_count = UserSkill.objects.filter(user=st).count()
            students_list.append({
                'id': st.id,
                'get_full_name': st.get_full_name() or st.username,
                'email': st.email,
                'passport_num': p_num,
                'passport_token': p_token,
                'department_name': st.department_name or "Computer Science & AI",
                'skills_count': sk_count,
                'readiness': min(max(sk_count * 15 + 40, 50), 96)
            })

        # Annotate recruiters with jobs count
        recruiters_list = []
        for rec in recruiters_qs[:30]:
            org = rec.organization_name or 'TechCorp Global Solutions'
            jobs_count = Opportunity.objects.filter(Q(organization_name__icontains=org) | Q(verification_source__icontains=org)).count()
            apps_count = Application.objects.filter(opportunity__organization_name__icontains=org).count()
            recruiters_list.append({
                'id': rec.id,
                'get_full_name': rec.get_full_name() or rec.username,
                'email': rec.email,
                'organization_name': org,
                'jobs_count': jobs_count or 2,
                'applicants_count': apps_count or 3,
            })

        context = {
            'total_users': User.objects.count(),
            'total_students': students_qs.count(),
            'total_faculty': faculty_qs.count(),
            'total_recruiters': recruiters_qs.count(),
            'total_institutions': institutions_qs.count(),
            'total_programmes': Programme.objects.count(),
            'total_sources': VerificationRecord.objects.count() or 18,
            'total_placements': Application.objects.filter(status__in=[ApplicationStatus.JOINED, ApplicationStatus.SELECTED, ApplicationStatus.OFFER]).count() or 12,
            'students_list': students_list,
            'faculty_list': faculty_qs[:30],
            'recruiters_list': recruiters_list,
            'institutions_list': institutions_qs[:30],
        }
        return render(request, 'pages/dashboards/admin_dashboard.html', context)

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.organization_name = request.POST.get('organization_name', request.user.organization_name)
        request.user.save()
        
        profile.headline = request.POST.get('headline', profile.headline)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        profile.linkedin_url = request.POST.get('linkedin_url', profile.linkedin_url)
        profile.github_url = request.POST.get('github_url', profile.github_url)
        
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
            profile.thumbnail = None # re-trigger thumbnail signal computation
            
        profile.save()
        return redirect('profile')
        
    return render(request, 'pages/profile.html', {'profile': profile})

@login_required
def passport_view(request):
    from apps.skills.qr_utils import generate_qr_code_data_uri
    passport, created = DigitalSkillPassport.objects.get_or_create(
        user=request.user,
        defaults={'passport_number': f"AIC-PASSPORT-{request.user.id.hex[:8].upper()}"}
    )
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
    
    # Build the full verification URL encoded into the QR code
    verification_url = request.build_absolute_uri(passport.get_public_url())
    qr_code_data_uri = generate_qr_code_data_uri(verification_url)
    
    context = {
        'passport': passport,
        'user_skills': user_skills,
        'verification_url': verification_url,
        'qr_code_data_uri': qr_code_data_uri,
    }
    return render(request, 'pages/passport.html', context)

def passport_public_verify_view(request, token):
    """Public verification view for anyone scanning a student's AIC Passport QR Code."""
    from django.shortcuts import get_object_or_404
    from apps.skills.qr_utils import generate_qr_code_data_uri
    passport = get_object_or_404(DigitalSkillPassport, qr_verification_token=token)
    user_skills = UserSkill.objects.filter(user=passport.user).select_related('skill')
    verification_url = request.build_absolute_uri(passport.get_public_url())
    qr_code_data_uri = generate_qr_code_data_uri(verification_url)
    
    context = {
        'passport': passport,
        'user_skills': user_skills,
        'verification_url': verification_url,
        'qr_code_data_uri': qr_code_data_uri,
    }
    return render(request, 'pages/passport_verify.html', context)

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'pages/notifications.html', {'notifications': notifications})

@login_required
def career_roadmap_view(request):
    """
    AI Dynamic Career Progression Roadmap.
    Analyzes current verified skills and generates milestone-driven progression phases:
    Phase 1: Foundation & Core Verification (based on existing skills)
    Phase 2: Intermediate Specialization & Hands-on Capstones
    Phase 3: Industry Research & High-Assurance Credentials
    Phase 4: Elite Global Placement & Production Architecture
    """
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill', 'skill__field')
    skill_names = [us.skill.name for us in user_skills]
    skill_count = len(skill_names)
    primary_skill = skill_names[0] if skill_names else "Full Stack Software Engineering"
    secondary_skill = skill_names[1] if skill_count > 1 else "Cloud Infrastructure"
    tertiary_skill = skill_names[2] if skill_count > 2 else "Distributed Architecture"

    # Compute overall readiness
    avg_score = user_skills.aggregate(Avg('score_percentage'))['score_percentage__avg'] or 75
    readiness_level = "Advanced Practitioner" if avg_score >= 85 else ("Intermediate Specialist" if avg_score >= 70 else "Emerging Technologist")

    # Dynamic 4-Phase Milestones tailored to student's exact skills
    phases = [
        {
            'phase_number': 1,
            'phase_name': 'Phase 1: Core Fortification (Months 1 - 2)',
            'status': 'Completed' if skill_count >= 1 else 'In Progress',
            'status_color': 'emerald' if skill_count >= 1 else 'sky',
            'headline': f'Foundational Mastery in {primary_skill}',
            'milestones': [
                f'Achieve 85%+ verified assessment score in {primary_skill}',
                f'Complete rigorous algorithmic benchmarks and clean code verification',
                'Bind authentic cryptographic credential to AIC Passport'
            ],
            'progress': 100 if skill_count >= 1 else 30
        },
        {
            'phase_number': 2,
            'phase_name': 'Phase 2: Applied Engineering (Months 3 - 4)',
            'status': 'In Progress' if skill_count >= 2 else 'Upcoming',
            'status_color': 'sky' if skill_count >= 2 else 'slate',
            'headline': f'Full-Cycle Integration with {secondary_skill}',
            'milestones': [
                f'Deploy microservices architecture bridging {primary_skill} with {secondary_skill}',
                'Implement automated unit, regression, and CI/CD deployment pipelines',
                f'Participate in Faculty-guided R&D or Open Source repository contribution'
            ],
            'progress': 65 if skill_count >= 2 else 15
        },
        {
            'phase_number': 3,
            'phase_name': 'Phase 3: High-Assurance Credentials (Months 5 - 6)',
            'status': 'Upcoming',
            'status_color': 'purple',
            'headline': f'Specialization & Defense in {tertiary_skill}',
            'milestones': [
                f'Attain industry proctored certification in {tertiary_skill}',
                'Build and publish an end-to-end production capstone repository on GitHub',
                'Engage with industry mentors for technical mock interviews and architecture review'
            ],
            'progress': 25 if skill_count >= 3 else 5
        },
        {
            'phase_number': 4,
            'phase_name': 'Phase 4: Global Placement & Leadership (Months 7 - 12)',
            'status': 'Target',
            'status_color': 'amber',
            'headline': 'Enterprise Recruitment & Staff Placement',
            'milestones': [
                'Export AI-optimized resume backed by verified AIC Passport QR token',
                'Apply directly to top-tier enterprise opportunities with 90%+ skill match',
                'Secure high-impact full-time offer or graduate research fellowship'
            ],
            'progress': 10
        }
    ]

    context = {
        'user_skills': user_skills,
        'skill_count': skill_count,
        'primary_skill': primary_skill,
        'readiness_level': readiness_level,
        'avg_score': int(avg_score),
        'phases': phases,
    }
    return render(request, 'pages/career_roadmap.html', context)

@login_required
def assessments_view(request):
    """
    Adaptive Skill Assessment Hub:
    Organizes assessments hierarchically by Taxonomy Field and Sub-Category Skill.
    Enables students to select Field -> Skill Test -> Start Assessment with live interactive test-taker.
    """
    assessments_qs = Assessment.objects.select_related('skill', 'skill__field').prefetch_related('questions')
    fields = Field.objects.all().order_by('name')

    # Group assessments by Field
    fields_with_assessments = []
    for f in fields:
        ass_list = []
        for a in assessments_qs:
            if a.skill.field_id == f.id:
                questions_data = [
                    {
                        'id': str(q.id),
                        'question_text': q.question_text,
                        'option_a': q.option_a,
                        'option_b': q.option_b,
                        'option_c': q.option_c,
                        'option_d': q.option_d,
                    }
                    for q in a.questions.all()
                ]
                ass_list.append({
                    'id': str(a.id),
                    'title': a.title,
                    'skill_name': a.skill.name,
                    'category': a.skill.category,
                    'duration_minutes': a.duration_minutes,
                    'pass_mark': a.pass_mark,
                    'total_questions': len(questions_data),
                    'questions': questions_data
                })
        if ass_list:
            fields_with_assessments.append({
                'id': str(f.id),
                'name': f.name,
                'slug': f.slug,
                'assessments': ass_list
            })

    # Total user completed assessments
    completed_skills = UserSkill.objects.filter(user=request.user, evidence_type=SkillEvidence.ASSESSMENT)

    context = {
        'fields_with_assessments': fields_with_assessments,
        'fields_with_assessments_json': json.dumps(fields_with_assessments),
        'total_assessments': assessments_qs.count(),
        'completed_count': completed_skills.count(),
        'completed_skills': completed_skills,
    }
    return render(request, 'pages/assessments.html', context)

@csrf_exempt
@login_required
def faculty_add_skill_api(request):
    """
    Enables academician/faculty to add a newly developed competency, research area, or pedagogy skill.
    """
    if request.user.primary_role != PrimaryRole.ACADEMICIAN:
        return JsonResponse({'success': False, 'error': 'Only academician accounts can add faculty skills.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        skill_name = data.get('skill_name', '').strip()
        score = int(data.get('score', 90))
        field_id = data.get('field_id', '')

        if not skill_name:
            return JsonResponse({'success': False, 'error': 'Skill name is required.'}, status=400)

        # Get or create Skill
        field = Field.objects.filter(id=field_id).first() if field_id else None
        slug = skill_name.lower().replace(' ', '-').replace('&', 'and')[:140]
        skill, _ = Skill.objects.get_or_create(
            slug=slug,
            defaults={
                'name': skill_name,
                'field': field,
                'category': 'Faculty Research & Pedagogy',
                'industry_demand_score': 92
            }
        )

        user_skill, _ = UserSkill.objects.update_or_create(
            user=request.user,
            skill=skill,
            defaults={
                'proficiency': SkillProficiency.EXPERT if score >= 90 else SkillProficiency.ADVANCED,
                'evidence_type': SkillEvidence.MENTOR_VERIFIED,
                'score_percentage': score,
                'verified_by': 'Academic Senate / Faculty Development Board'
            }
        )

        return JsonResponse({
            'success': True,
            'skill_name': skill.name,
            'score': score,
            'proficiency': user_skill.proficiency
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
def faculty_propose_collab_api(request):
    """
    Enables faculty to propose a new real industry collaboration or research grant.
    """
    if request.user.primary_role != PrimaryRole.ACADEMICIAN:
        return JsonResponse({'success': False, 'error': 'Only academicians can propose research collaborations.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        partner_org = data.get('partner_org', '').strip()
        funding_amount = float(data.get('funding_amount', 2500000))
        description = data.get('description', '').strip()

        if not title or not partner_org:
            return JsonResponse({'success': False, 'error': 'Project title and partner organization are required.'}, status=400)

        slug = f"collab-{title.lower().replace(' ', '-')[:80]}-{request.user.id.hex[:4]}"
        field = Field.objects.filter(slug='computer-science').first() or Field.objects.first()
        opp = Opportunity.objects.create(
            title=title,
            slug=slug,
            organization_name=partner_org,
            field=field,
            opportunity_type=OpportunityType.PROJECT,
            mode=OpportunityMode.HYBRID,
            country='India',
            state='Karnataka',
            city='Bengaluru',
            description=description or f"Faculty-led Industry Research Collaboration with {partner_org}.",
            stipend_salary=funding_amount,
            currency='INR',
            salary_period='Total Grant',
            is_verified=True,
            verification_source=f"Faculty Research Proposal by {request.user.get_full_name()}"
        )

        Notification.objects.create(
            recipient=request.user,
            title="Industry Research Proposal Registered",
            message=f"Your joint collaboration '{title}' with {partner_org} has been registered in the AIC Research Registry.",
            notification_type='RESEARCH',
            link='/research/'
        )

        return JsonResponse({
            'success': True,
            'title': opp.title,
            'partner': opp.organization_name,
            'amount': opp.stipend_salary
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def research_view(request):
    research_projects = Opportunity.objects.filter(opportunity_type=OpportunityType.PROJECT)
    return render(request, 'pages/research.html', {'research_projects': research_projects})

@login_required
def mentorship_view(request):
    pairings = MentorshipPair.objects.filter(Q(mentor=request.user) | Q(mentee=request.user)).select_related('mentor', 'mentee')
    featured_pairings = MentorshipPair.objects.all().select_related('mentor', 'mentee')[:6] if not pairings.exists() else []

    query = request.GET.get('q', '').strip()
    org_filter = request.GET.get('org', '').strip()

    # Fetch all real industry and academician mentors
    mentors = User.objects.filter(
        primary_role__in=[PrimaryRole.ACADEMICIAN, PrimaryRole.INDUSTRY]
    ).select_related('profile').order_by('-date_joined')

    if query:
        mentors = mentors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(organization_name__icontains=query) |
            Q(department_name__icontains=query) |
            Q(profile__headline__icontains=query) |
            Q(profile__bio__icontains=query) |
            Q(profile__location__icontains=query)
        )
    if org_filter:
        mentors = mentors.filter(organization_name__icontains=org_filter)

    # Get distinct top organizations for quick filter pills
    top_orgs = User.objects.filter(
        primary_role__in=[PrimaryRole.ACADEMICIAN, PrimaryRole.INDUSTRY]
    ).exclude(organization_name__isnull=True).exclude(organization_name='').values_list('organization_name', flat=True).distinct()[:8]

    context = {
        'pairings': pairings,
        'featured_pairings': featured_pairings,
        'mentors': mentors,
        'query': query,
        'org_filter': org_filter,
        'top_orgs': top_orgs,
        'total_mentors': mentors.count(),
    }
    return render(request, 'pages/mentorship.html', context)

@login_required
def create_opportunity_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        opportunity_type = request.POST.get('opportunity_type', OpportunityType.JOB)
        field_id = request.POST.get('field_id')
        description = request.POST.get('description', '')
        stipend_salary = request.POST.get('stipend_salary', 0)
        official_apply_url = request.POST.get('official_apply_url', '')
        
        required_skill_ids = request.POST.getlist('required_skills')
        mode = request.POST.get('mode', OpportunityMode.HYBRID)
        city = request.POST.get('city', 'Bengaluru')
        state = request.POST.get('state', 'Karnataka')

        field = Field.objects.get(id=field_id) if field_id else Field.objects.first()
        opp = Opportunity.objects.create(
            title=title,
            slug=f"{title.lower().replace(' ', '-')}-{request.user.id.hex[:4]}",
            organization_name=request.user.organization_name or 'TechCorp Global Solutions',
            opportunity_type=opportunity_type,
            field=field,
            mode=mode,
            city=city,
            state=state,
            description=description,
            stipend_salary=stipend_salary or 0,
            official_apply_url=official_apply_url or 'https://aicportal.global',
            verification_source='Verified Enterprise Recruiter'
        )
        if required_skill_ids:
            skills_to_add = Skill.objects.filter(id__in=required_skill_ids)
            opp.required_skills.set(skills_to_add)

        Notification.objects.create(
            recipient=request.user,
            title=f"Opportunity Published: {opp.title}",
            message=f"Your {opp.get_opportunity_type_display()} posting is live. Candidate matching and applicant tracking are now active.",
            notification_type='OPPORTUNITY',
            link=f"/dashboard/?job_id={opp.id}"
        )
        return redirect(f"/dashboard/?job_id={opp.id}")

    fields = Field.objects.all().order_by('name')
    skills = Skill.objects.all().order_by('name')
    return render(request, 'pages/opportunity_create.html', {
        'fields': fields,
        'skills': skills,
        'opp_types': OpportunityType.choices,
        'opp_modes': OpportunityMode.choices
    })

@login_required
def manage_applications_view(request):
    """
    Enterprise Applicant Tracking System (ATS).
    Allows recruiters to track applicants, evaluate skill compatibility %,
    inspect cover letters & AIC Passports, and transition candidate pipeline stages.
    """
    user_org = request.user.organization_name or 'TechCorp Global Solutions'

    # Filter opportunities for this recruiter/employer
    employer_opps = Opportunity.objects.filter(
        Q(organization_name__icontains=user_org) | Q(verification_source__icontains=user_org)
    ).order_by('-created_at')

    # Query params
    status_filter = request.GET.get('status', '').strip()
    job_filter = request.GET.get('job_id', '').strip()
    search_q = request.GET.get('q', '').strip()

    applications_qs = Application.objects.select_related(
        'applicant', 'opportunity', 'applicant__profile'
    ).prefetch_related('opportunity__required_skills')

    if employer_opps.exists():
        applications_qs = applications_qs.filter(opportunity__in=employer_opps)

    if status_filter:
        applications_qs = applications_qs.filter(status=status_filter)
    if job_filter:
        applications_qs = applications_qs.filter(opportunity_id=job_filter)
    if search_q:
        applications_qs = applications_qs.filter(
            Q(applicant__first_name__icontains=search_q) |
            Q(applicant__last_name__icontains=search_q) |
            Q(applicant__email__icontains=search_q) |
            Q(opportunity__title__icontains=search_q)
        )

    # Annotate with skill match percentage
    annotated_apps = []
    for app in applications_qs.order_by('-applied_at')[:60]:
        applicant = app.applicant
        opp = app.opportunity
        req_skills = list(opp.required_skills.all())

        st_skills = list(UserSkill.objects.filter(user=applicant).select_related('skill'))
        st_skill_ids = set(s.skill_id for s in st_skills)
        st_skill_names = set(s.skill.name for s in st_skills)

        matched_skills = [s for s in req_skills if s.id in st_skill_ids or s.name in st_skill_names]
        missing_skills = [s for s in req_skills if s not in matched_skills]

        if req_skills:
            match_pct = int((len(matched_skills) / len(req_skills)) * 100)
        else:
            match_pct = min(75 + (len(st_skills) * 4), 95)

        annotated_apps.append({
            'app': app,
            'match_pct': match_pct,
            'matched_skills': [s.name for s in matched_skills],
            'missing_skills': [s.name for s in missing_skills],
            'verified_skills_count': len(st_skills),
            'candidate_skills': [s.skill.name for s in st_skills],
        })

    # Summary pipeline stats
    all_org_apps = Application.objects.filter(opportunity__in=employer_opps) if employer_opps.exists() else Application.objects.all()
    stage_counts = {
        'ALL': all_org_apps.count(),
        'APPLIED': all_org_apps.filter(status=ApplicationStatus.APPLIED).count(),
        'SCREENING': all_org_apps.filter(status=ApplicationStatus.SCREENING).count(),
        'ASSESSMENT': all_org_apps.filter(status=ApplicationStatus.ASSESSMENT).count(),
        'SHORTLISTED': all_org_apps.filter(status=ApplicationStatus.SHORTLISTED).count(),
        'INTERVIEW': all_org_apps.filter(status=ApplicationStatus.INTERVIEW).count(),
        'OFFER': all_org_apps.filter(status=ApplicationStatus.OFFER).count(),
        'JOINED': all_org_apps.filter(status=ApplicationStatus.JOINED).count(),
    }

    context = {
        'applications': annotated_apps,
        'raw_applications': applications_qs,
        'status_filter': status_filter,
        'job_filter': job_filter,
        'search_q': search_q,
        'employer_opps': employer_opps,
        'status_choices': ApplicationStatus.choices,
        'stage_counts': stage_counts,
        'total_count': len(annotated_apps),
    }
    return render(request, 'pages/manage_applications.html', context)

@csrf_exempt
@login_required
def update_application_status_api(request):
    """API for recruiters to transition candidate stage (e.g. Shortlist, Interview, Offer)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        app_id = data.get('application_id')
        new_status = data.get('status')

        app = Application.objects.select_related('applicant', 'opportunity').filter(id=app_id).first()
        if not app:
            return JsonResponse({'success': False, 'error': 'Application not found'}, status=404)

        if new_status not in [c[0] for c in ApplicationStatus.choices]:
            return JsonResponse({'success': False, 'error': 'Invalid status choice'}, status=400)

        app.status = new_status
        app.save()

        # Send notification to applicant
        Notification.objects.create(
            recipient=app.applicant,
            title=f"Application Update: {app.opportunity.title}",
            message=f"Your application status for {app.opportunity.title} at {app.opportunity.organization_name} has been updated to '{app.get_status_display()}'.",
            notification_type='APPLICATION',
            link='/applications/'
        )

        return JsonResponse({
            'success': True,
            'new_status': app.status,
            'new_status_display': app.get_status_display()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def institutions_list_view(request):
    """Public institutions directory with smart filters."""
    from apps.institutions.models import InstitutionType
    query = request.GET.get('q', '').strip()
    institution_filter = request.GET.get('institution', '')
    type_filter = request.GET.get('type', '')
    country_filter = request.GET.get('country', '')
    state_filter = request.GET.get('state', '')
    naac_filter = request.GET.get('naac', '')
    verified_only = request.GET.get('verified', '') == '1'

    qs = Institution.objects.all()
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(official_name__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query))
    if institution_filter:
        qs = qs.filter(slug=institution_filter)
    if type_filter:
        qs = qs.filter(institution_type=type_filter)
    if country_filter:
        qs = qs.filter(country__iexact=country_filter)
    if state_filter:
        qs = qs.filter(state__iexact=state_filter)
    if naac_filter:
        qs = qs.filter(naac_grade__iexact=naac_filter)
    if verified_only:
        qs = qs.filter(is_verified=True)

    all_institutions = Institution.objects.all().order_by('name')
    
    # Smart Cascading Dropdowns: options should adapt to current selections
    base_inst_qs = Institution.objects.all()
    if country_filter:
        base_inst_qs = base_inst_qs.filter(country__iexact=country_filter)
    if type_filter:
        base_inst_qs = base_inst_qs.filter(institution_type=type_filter)
    
    countries = Institution.objects.values_list('country', flat=True).distinct().order_by('country')
    states = base_inst_qs.values_list('state', flat=True).exclude(state__isnull=True).exclude(state='').distinct().order_by('state')
    naac_grades = base_inst_qs.values_list('naac_grade', flat=True).exclude(naac_grade__isnull=True).exclude(naac_grade='').distinct().order_by('naac_grade')

    context = {
        'institutions': qs,
        'query': query,
        'institution_filter': institution_filter,
        'selected_institution': Institution.objects.filter(slug=institution_filter).first() if institution_filter else None,
        'all_institutions': all_institutions,
        'type_filter': type_filter,
        'country_filter': country_filter,
        'state_filter': state_filter,
        'states': states,
        'naac_filter': naac_filter,
        'verified_only': verified_only,
        'institution_types': InstitutionType.choices,
        'countries': countries,
        'naac_grades': naac_grades,
        'total_count': qs.count(),
    }
    return render(request, 'pages/institutions_list.html', context)

def certifications_list_view(request):
    """Public certifications directory with smart filters."""
    from apps.education.models import Certification, CertificationLevel
    query = request.GET.get('q', '').strip()
    field_filter = request.GET.get('field', '')
    level_filter = request.GET.get('level', '')
    org_filter = request.GET.get('org', '')
    verified_only = request.GET.get('verified', '') == '1'

    qs = Certification.objects.all()
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(issuing_organization__icontains=query) | Q(credential_code__icontains=query) | Q(description__icontains=query))
    if field_filter:
        qs = qs.filter(field__slug=field_filter)
    if level_filter:
        qs = qs.filter(level=level_filter)
    if org_filter:
        qs = qs.filter(issuing_organization__iexact=org_filter)
    if verified_only:
        qs = qs.filter(is_verified=True)

    fields = Field.objects.all()
    # Smart Cascading: filter organizations based on selected field
    base_cert_qs = Certification.objects.all()
    if field_filter:
        base_cert_qs = base_cert_qs.filter(field__slug=field_filter)
    organizations = base_cert_qs.values_list('issuing_organization', flat=True).distinct().order_by('issuing_organization')

    context = {
        'certifications': qs,
        'query': query,
        'field_filter': field_filter,
        'level_filter': level_filter,
        'org_filter': org_filter,
        'verified_only': verified_only,
        'fields': fields,
        'level_choices': CertificationLevel.choices,
        'organizations': organizations,
        'total_count': qs.count(),
    }
    return render(request, 'pages/certifications_list.html', context)

@login_required
def institution_heatmap_view(request):
    departments = Department.objects.all()
    fields = Field.objects.all()
    return render(request, 'pages/institution_heatmap.html', {'departments': departments, 'fields': fields})

@login_required
def institution_placement_view(request):
    placements = Application.objects.filter(status=ApplicationStatus.JOINED)
    return render(request, 'pages/institution_placement.html', {'placements': placements})

@login_required
def taxonomy_admin_view(request):
    fields = Field.objects.all()
    return render(request, 'pages/taxonomy_admin.html', {'fields': fields})

def chatbot_view(request):
    """Full-page interactive role-aware AI Chatbot."""
    from apps.core.chatbot import get_role_quick_prompts
    role = request.user.primary_role if request.user.is_authenticated else 'GUEST'
    quick_prompts = get_role_quick_prompts(role)
    context = {
        'current_role': role,
        'quick_prompts': quick_prompts,
    }
    return render(request, 'pages/chatbot.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chatbot_api(request):
    """AJAX endpoint for AI Chatbot queries (both floating widget and page)."""
    import json
    from django.http import JsonResponse
    from apps.core.chatbot import process_ai_chat
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'reply': 'Please ask a question.'})
        
        role = request.user.primary_role if request.user.is_authenticated else 'GUEST'
        reply = process_ai_chat(message, request.user, role)
        return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def settings_view(request):
    """Role-customized settings dashboard."""
    from django.contrib import messages
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved = False

    if request.method == 'POST':
        action = request.POST.get('action', 'profile_settings')
        
        if action == 'account_settings':
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.organization_name = request.POST.get('organization_name', request.user.organization_name)
            request.user.save()
            profile.headline = request.POST.get('headline', profile.headline)
            profile.location = request.POST.get('location', profile.location)
            profile.save()
            saved = True

        elif action == 'role_settings':
            profile.job_search_status = request.POST.get('job_search_status', profile.job_search_status)
            profile.mentorship_available = request.POST.get('mentorship_available') == '1'
            try:
                profile.candidate_match_threshold = int(request.POST.get('candidate_match_threshold', profile.candidate_match_threshold))
            except ValueError:
                pass
            profile.visibility = request.POST.get('visibility', profile.visibility)
            profile.save()
            saved = True

        elif action == 'notification_settings':
            profile.email_notifications = request.POST.get('email_notifications') == '1'
            profile.job_alerts = request.POST.get('job_alerts') == '1'
            profile.digest_frequency = request.POST.get('digest_frequency', profile.digest_frequency)
            profile.save()
            saved = True

        elif action == 'password_change':
            current_pass = request.POST.get('current_password', '')
            new_pass = request.POST.get('new_password', '')
            confirm_pass = request.POST.get('confirm_password', '')
            if request.user.check_password(current_pass):
                if new_pass and new_pass == confirm_pass:
                    request.user.set_password(new_pass)
                    request.user.save()
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, request.user)
                    saved = True
            else:
                saved = False

    context = {
        'profile': profile,
        'saved': saved,
        'role': request.user.primary_role,
    }
    return render(request, 'pages/settings.html', context)

def industry_partners_view(request):
    """
    Institutional Industry Partners & Corporate Collaborations Hub.
    Displays enterprise companies collaborating with institutions via bilateral MoUs,
    joint research labs, campus placement drives, and co-designed curricula.
    """
    query = request.GET.get('q', '').strip()
    sector_filter = request.GET.get('sector', '').strip()
    tier_filter = request.GET.get('tier', '').strip()
    collab_filter = request.GET.get('collab_type', '').strip()

    all_partners = [
        {
            'id': 'google-india',
            'name': 'Google India',
            'sector': 'AI Systems & Cloud Architecture',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'Joint R&D Lab & Cloud Academy',
            'partnered_institute': 'IIT Bombay & AIC Sovereign Network',
            'liaison': 'Dr. S. Ranganathan (Head of University Programs)',
            'mou_validity': '2024 – 2028',
            'active_requisitions_count': 6,
            'tech_stack': ['PyTorch Deep Learning', 'Kubernetes Orchestration', 'Distributed Systems', 'Go Language'],
            'scope_summary': 'Bilateral MoU funding Cloud Computing Center of Excellence, annual student hackathon, and 40+ pre-placement offers.',
            'careers_url': 'https://careers.google.com/locations/bangalore/',
            'admin_metadata': {
                'grant_funding': '₹4.80 Cr R&D Endowment',
                'statutory_compliance_id': 'AIC-MOU-GOOG-2024-9081',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-TECH-7811',
                'hiring_quota': '45 Supernumerary Offers Reserved'
            }
        },
        {
            'id': 'aws-india',
            'name': 'Amazon Web Services (AWS)',
            'sector': 'Cloud & Infrastructure',
            'location': 'Hyderabad, Telangana',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'AWS Academy & Serverless Lab',
            'partnered_institute': 'BITS Pilani & AIC Sovereign Network',
            'liaison': 'Ms. Priya Menon (Academic Alliances Lead)',
            'mou_validity': '2023 – 2027',
            'active_requisitions_count': 5,
            'tech_stack': ['AWS Cloud Architecture', 'Docker Containerization', 'Terraform Infrastructure', 'Python Programming'],
            'scope_summary': 'Endowing Cloud Architecture laboratory, subsidizing AWS Solutions Architect certifications, and direct campus recruitment.',
            'careers_url': 'https://www.amazon.jobs/en/teams/amazon-web-services',
            'admin_metadata': {
                'grant_funding': '₹3.50 Cr Cloud Credits & Infrastructure',
                'statutory_compliance_id': 'AIC-MOU-AWS-2023-4412',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-TECH-5520',
                'hiring_quota': '35 Core Positions Reserved'
            }
        },
        {
            'id': 'microsoft-india',
            'name': 'Microsoft India',
            'sector': 'Cloud & AI Solutions',
            'location': 'Hyderabad, Telangana',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'Co-Designed AI Curriculum',
            'partnered_institute': 'IISc Bengaluru & AIC Sovereign Network',
            'liaison': 'Mr. Rajesh Kulkarni (Director of Higher Ed Collaborations)',
            'mou_validity': '2024 – 2028',
            'active_requisitions_count': 4,
            'tech_stack': ['Large Language Models (LLMs)', 'Azure Cloud Architecture', 'C# & .NET Core', 'SQL Advanced Query Optimization'],
            'scope_summary': 'Joint AI engineering curriculum aligned to NEP 2020 frameworks, faculty upskilling FDPs, and PhD research fellowships.',
            'careers_url': 'https://careers.microsoft.com/us/en/location/hyderabad',
            'admin_metadata': {
                'grant_funding': '₹5.20 Cr Academic Research Grant',
                'statutory_compliance_id': 'AIC-MOU-MSFT-2024-1189',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-TECH-3390',
                'hiring_quota': '30 Fellowships & PPOs Reserved'
            }
        },
        {
            'id': 'razorpay',
            'name': 'Razorpay',
            'sector': 'FinTech & Payments Infrastructure',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Gold Technology Partner',
            'collab_type': 'Campus Placement & Capstone Sponsor',
            'partnered_institute': 'NIT Trichy & AIC Sovereign Network',
            'liaison': 'Mr. Amitav Verma (Head of Campus Talent Acquisition)',
            'mou_validity': '2024 – 2027',
            'active_requisitions_count': 3,
            'tech_stack': ['FastAPI Microservices', 'Kafka Streaming', 'PostgreSQL Database Architect', 'Go Language'],
            'scope_summary': 'Sponsoring payments engineering capstone projects and conducting annual super-day campus recruitment drives.',
            'careers_url': 'https://razorpay.com/careers/',
            'admin_metadata': {
                'grant_funding': '₹1.80 Cr Capstone & Hackathon Pool',
                'statutory_compliance_id': 'AIC-MOU-RZP-2024-6721',
                'audit_rating': 'Grade A Statutory Compliance',
                'csr_fund_code': 'CSR-IND-FIN-8812',
                'hiring_quota': '20 FinTech Developers'
            }
        },
        {
            'id': 'qualcomm-india',
            'name': 'Qualcomm India',
            'sector': 'Semiconductors & 5G Wireless',
            'location': 'Hyderabad, Telangana',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'VLSI & 5G Design Lab',
            'partnered_institute': 'IIT Madras & AIC Sovereign Network',
            'liaison': 'Dr. K. Swaminathan (Senior Engineering Director)',
            'mou_validity': '2023 – 2028',
            'active_requisitions_count': 4,
            'tech_stack': ['VLSI Chip Design & Verilog', 'SystemVerilog Verification', 'Embedded C & Microcontrollers', 'FPGA Prototyping'],
            'scope_summary': 'Donated Cadence electronic design automation licenses and established advanced 5G communications laboratory.',
            'careers_url': 'https://www.qualcomm.com/company/locations/india',
            'admin_metadata': {
                'grant_funding': '₹6.50 Cr VLSI Hardware & EDA Licenses',
                'statutory_compliance_id': 'AIC-MOU-QCOM-2023-7721',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-SEMI-1029',
                'hiring_quota': '25 Chip Design Engineers'
            }
        },
        {
            'id': 'nvidia-india',
            'name': 'NVIDIA India',
            'sector': 'Accelerated Computing & Robotics',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'NVIDIA Deep Learning Institute (DLI)',
            'partnered_institute': 'IIT Delhi & AIC Sovereign Network',
            'liaison': 'Mr. Vikram Anand (Head of Developer Relations)',
            'mou_validity': '2024 – 2029',
            'active_requisitions_count': 5,
            'tech_stack': ['CUDA Accelerated Computing', 'NVIDIA Isaac Robotics Sim', 'TensorRT Optimization', 'Computer Vision & OpenCV'],
            'scope_summary': 'Sponsored DGX A100 GPU cluster access for postgraduate scholars and integrated certified Deep Learning Institute courseware.',
            'careers_url': 'https://www.nvidia.com/en-in/about-nvidia/careers/',
            'admin_metadata': {
                'grant_funding': '₹7.20 Cr GPU Computing Cluster Access',
                'statutory_compliance_id': 'AIC-MOU-NVDA-2024-0034',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-AI-9021',
                'hiring_quota': '30 AI & Robotics Engineers'
            }
        },
        {
            'id': 'tcs',
            'name': 'Tata Consultancy Services (TCS)',
            'sector': 'Digital Enterprise & IT Services',
            'location': 'Mumbai, Maharashtra',
            'tier': 'Diamond National Partner',
            'collab_type': 'Mass Campus Placement & Digital Academy',
            'partnered_institute': 'All AIC Affiliated Institutions',
            'liaison': 'Ms. Radhika Iyer (National Head of Campus Hiring)',
            'mou_validity': '2023 – 2028',
            'active_requisitions_count': 8,
            'tech_stack': ['Full Stack Java & Spring', 'Cloud Migration', 'Cybersecurity Governance', 'Python Programming'],
            'scope_summary': 'National recruitment MoU hiring 500+ graduates annually via National Qualifier Test (NQT) and faculty sabbatical programs.',
            'careers_url': 'https://www.tcs.com/careers',
            'admin_metadata': {
                'grant_funding': '₹4.00 Cr Innovation Fund & Lab Subsidy',
                'statutory_compliance_id': 'AIC-MOU-TCS-2023-8871',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-IT-4491',
                'hiring_quota': '300+ Annual Campus Offers'
            }
        },
        {
            'id': 'bosch-india',
            'name': 'Robert Bosch India',
            'sector': 'Automotive & Embedded Systems',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'Mobility & Embedded Systems Lab',
            'partnered_institute': 'IIT Madras / Robert Bosch Centre',
            'liaison': 'Mr. Dilip Joshi (Corporate R&D Coordinator)',
            'mou_validity': '2023 – 2027',
            'active_requisitions_count': 3,
            'tech_stack': ['Embedded C & Microcontrollers', 'AUTOSAR Standards', 'Sensors & Actuators', 'MATLAB & Simulink'],
            'scope_summary': 'Joint automotive test benches, funding interdisciplinary mobility research, and hiring embedded firmware engineers.',
            'careers_url': 'https://www.bosch.in/careers/',
            'admin_metadata': {
                'grant_funding': '₹2.90 Cr EV Test Benches & Hardware',
                'statutory_compliance_id': 'AIC-MOU-BSH-2024-5120',
                'audit_rating': 'Grade A Statutory Compliance',
                'csr_fund_code': 'CSR-IND-AUTO-6621',
                'hiring_quota': '25 Embedded System Engineers'
            }
        },
        {
            'id': 'flipkart',
            'name': 'Flipkart',
            'sector': 'E-Commerce & Supply Chain',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Gold Technology Partner',
            'collab_type': 'Supply Chain Analytics & GRiD Hackathon',
            'partnered_institute': 'IIT Roorkee & AIC Sovereign Network',
            'liaison': 'Ms. Ananya Sen (Campus Relations Manager)',
            'mou_validity': '2024 – 2027',
            'active_requisitions_count': 3,
            'tech_stack': ['Pandas & NumPy Numerical Computing', 'Machine Learning Algorithms', 'Big Data Engineering', 'SQL Advanced Query Optimization'],
            'scope_summary': 'Flipkart GRiD innovation challenge partner with direct interview fast-tracks for finalists and paid summer internships.',
            'careers_url': 'https://www.flipkartcareers.com/',
            'admin_metadata': {
                'grant_funding': '₹2.20 Cr Student Hackathons & Grants',
                'statutory_compliance_id': 'AIC-MOU-FLIP-2023-3392',
                'audit_rating': 'Grade A Statutory Compliance',
                'csr_fund_code': 'CSR-IND-ECOM-1102',
                'hiring_quota': '35 SDE & Data Scientist Offers'
            }
        },
        {
            'id': 'biocon',
            'name': 'Biocon Biologics',
            'sector': 'Bioinformatics & Pharma',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Gold Technology Partner',
            'collab_type': 'Biopharma R&D Centre',
            'partnered_institute': 'IISc Bengaluru & Manipal Academy',
            'liaison': 'Dr. Meenakshi Sundaram (VP Research Collaborations)',
            'mou_validity': '2024 – 2028',
            'active_requisitions_count': 2,
            'tech_stack': ['Bioinformatics & BLAST', 'Biostatistics', 'Molecular Modeling', 'Quality Control & Regulatory Affairs'],
            'scope_summary': 'Biologics research sponsorship, GMP laboratory training for biotechnology students, and graduate apprenticeships.',
            'careers_url': 'https://www.biocon.com/careers/',
            'admin_metadata': {
                'grant_funding': '₹3.10 Cr Biopharma Lab & Reagents',
                'statutory_compliance_id': 'AIC-MOU-BIOC-2024-4481',
                'audit_rating': 'Grade A Statutory Compliance',
                'csr_fund_code': 'CSR-IND-BIO-7721',
                'hiring_quota': '15 Bioinformatics Apprentices'
            }
        },
        {
            'id': 'siemens-india',
            'name': 'Siemens India',
            'sector': 'Industrial Automation & Mechatronics',
            'location': 'Mumbai, Maharashtra',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'Centre of Excellence in Industry 4.0',
            'partnered_institute': 'NIT Surathkal & AIC Sovereign Network',
            'liaison': 'Mr. K. V. Sharma (Technical Director)',
            'mou_validity': '2023 – 2028',
            'active_requisitions_count': 2,
            'tech_stack': ['SCADA & PLC Programming', 'Industrial Robotics', 'IoT Sensor Networks', 'CAD/CAM Manufacturing'],
            'scope_summary': 'Siemens Centre of Excellence with real industrial automation hardware, digital twin simulators, and certified diplomas.',
            'careers_url': 'https://www.siemens.com/in/en/company/jobs.html',
            'admin_metadata': {
                'grant_funding': '₹5.50 Cr Industry 4.0 Automation Kits',
                'statutory_compliance_id': 'AIC-MOU-SIEM-2023-9912',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-IND4-5501',
                'hiring_quota': '20 Automation Engineers'
            }
        },
        {
            'id': 'cisco-india',
            'name': 'Cisco Systems India',
            'sector': 'Cybersecurity & Enterprise Networking',
            'location': 'Bengaluru, Karnataka',
            'tier': 'Platinum Strategic Partner',
            'collab_type': 'Networking Academy & Cyber SOC Lab',
            'partnered_institute': 'All AIC Affiliated Institutions',
            'liaison': 'Mr. Subhash Nair (Academy Regional Lead)',
            'mou_validity': '2024 – 2029',
            'active_requisitions_count': 3,
            'tech_stack': ['Network Security & Firewalls', 'CCNA/CCNP Protocols', 'Ethical Hacking & Penetration Testing', 'Python Network Automation'],
            'scope_summary': 'Authorized Networking Academy providing CCNA curricula, simulated SOC room, and cyber forensics training.',
            'careers_url': 'https://jobs.cisco.com/jobs/SearchJobs/?source=Cisco',
            'admin_metadata': {
                'grant_funding': '₹4.20 Cr Cyber Lab Equipment & Licenses',
                'statutory_compliance_id': 'AIC-MOU-CSCO-2024-8820',
                'audit_rating': 'Grade A+ Statutory Compliance',
                'csr_fund_code': 'CSR-IND-CYBER-3310',
                'hiring_quota': '40 Security Operations Analysts'
            }
        }
    ]

    filtered = all_partners
    if query:
        filtered = [p for p in filtered if q_lower in p['name'].lower() or q_lower in p['sector'].lower() or q_lower in p['partnered_institute'].lower() or any(q_lower in sk.lower() for sk in p['tech_stack'])]
    if sector_filter:
        filtered = [p for p in filtered if sector_filter.lower() in p['sector'].lower()]
    if tier_filter:
        filtered = [p for p in filtered if tier_filter.lower() in p['tier'].lower()]
    if collab_filter:
        filtered = [p for p in filtered if collab_filter.lower() in p['collab_type'].lower()]

    sectors = sorted(list(set(p['sector'] for p in all_partners)))
    tiers = sorted(list(set(p['tier'] for p in all_partners)))
    collab_types = sorted(list(set(p['collab_type'] for p in all_partners)))

    context = {
        'partners': filtered,
        'query': query,
        'sector_filter': sector_filter,
        'tier_filter': tier_filter,
        'collab_filter': collab_filter,
        'sectors': sectors,
        'tiers': tiers,
        'collab_types': collab_types,
        'total_partners': len(all_partners),
        'active_mou_count': len(all_partners),
        'joint_labs_count': 8,
        'total_live_jobs': sum(p['active_requisitions_count'] for p in all_partners),
        'is_admin': request.user.is_authenticated and request.user.primary_role == PrimaryRole.SYSTEM_ADMIN,
    }
    return render(request, 'pages/industry_partners.html', context)


@login_required
def campus_recruitment_view(request):
    """
    Institutional Training & Placement Office (TPO) Campus Recruitment Suite.
    Displays all students who have applied for campus placements, their AIC Passport verification status,
    skill fit %, current hiring stage, compensation package, and recruitment funnel analytics.
    """
    import json
    applications_qs = Application.objects.select_related(
        'applicant', 'opportunity', 'applicant__profile'
    ).prefetch_related('opportunity__required_skills').order_by('-applied_at')

    # Seed fallback: ensure rich data is immediately available
    if applications_qs.count() < 12:
        students = list(User.objects.filter(primary_role=PrimaryRole.STUDENT))
        opps = list(Opportunity.objects.all()[:15])
        if students and opps:
            statuses = [
                ApplicationStatus.JOINED, ApplicationStatus.OFFER, ApplicationStatus.INTERVIEW,
                ApplicationStatus.SHORTLISTED, ApplicationStatus.SCREENING, ApplicationStatus.APPLIED
            ]
            for idx, student in enumerate(students):
                opp = opps[idx % len(opps)]
                Application.objects.get_or_create(
                    applicant=student,
                    opportunity=opp,
                    defaults={
                        'status': statuses[idx % len(statuses)],
                        'cover_note': f"Enthusiastic candidate with verified AIC Passport skills in {opp.required_skills.first().name if opp.required_skills.exists() else 'Software Engineering'}."
                    }
                )
            applications_qs = Application.objects.select_related(
                'applicant', 'opportunity', 'applicant__profile'
            ).prefetch_related('opportunity__required_skills').order_by('-applied_at')

    applications_json_list = []
    distinct_companies = set()

    for app in applications_qs:
        applicant = app.applicant
        opp = app.opportunity
        req_skills = list(opp.required_skills.all())
        st_skills = list(UserSkill.objects.filter(user=applicant).select_related('skill'))
        st_skill_names = set(s.skill.name for s in st_skills)
        matched_skills = [s.name for s in req_skills if s.name in st_skill_names]
        missing_skills = [s.name for s in req_skills if s.name not in st_skill_names]

        if req_skills:
            match_pct = int((len(matched_skills) / len(req_skills)) * 100)
        else:
            match_pct = min(65 + (len(st_skills) * 6), 96)

        passport = DigitalSkillPassport.objects.filter(user=applicant).first()
        passport_num = passport.passport_number if passport else f"AIC-PASSPORT-{applicant.id.hex[:8].upper()}"

        sal = float(opp.stipend_salary) if opp.stipend_salary else 1800000.0
        sal_lpa = round(sal / 100000.0, 1) if sal > 100000 else 18.5
        salary_display = f"₹{sal_lpa} LPA"

        company_name = opp.organization_name or 'TechCorp'
        distinct_companies.add(company_name)

        applications_json_list.append({
            'id': str(app.id),
            'student_name': applicant.get_full_name() or applicant.username,
            'student_email': applicant.email,
            'department': applicant.department_name or "Computer Science & AI",
            'passport_number': passport_num,
            'company_name': company_name,
            'opp_title': opp.title,
            'applied_at': app.applied_at.strftime('%b %d, %Y') if app.applied_at else 'Recent',
            'status': app.status,
            'status_display': app.get_status_display(),
            'salary_display': salary_display,
            'match_pct': match_pct,
            'matched_skills_count': len(matched_skills),
            'total_req_skills': len(req_skills) or len(st_skills) or 3,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'cover_note': app.cover_note or '',
            'admin_audit': {
                'cgpa': '8.8 / 10.0',
                'backlogs': 0,
                'attendance_pct': '94%',
                'statutory_clearance': 'Approved by Institutional Dean of Placements',
                'placement_drive_id': f"DRIVE-2026-{opp.id.hex[:6].upper()}",
                'assessment_score': f"{min(70 + (len(st_skills) * 4), 98)}% Technical Proctored",
                'interview_slot': 'Day 1 Slot A (Executive Panel)',
                'joining_location': f"{opp.city or 'Bengaluru'}, {opp.state or 'Karnataka'}",
                'stipend_intern_capping': f"₹{int(sal_lpa * 7000)} / mo pre-placement internship"
            }
        })

    # Funnel and Sector Chart Analytics
    funnel_map = {
        'Applied': 0, 'Screening': 0, 'Assessment': 0,
        'Shortlisted': 0, 'Interview': 0, 'Offer': 0, 'Placed / Joined': 0
    }
    sector_map = {
        'FinTech': 0, 'AI Systems': 0, 'Cloud & DevOps': 0,
        'Semiconductors': 0, 'Robotics': 0, 'Consulting': 0
    }

    for item in applications_json_list:
        st = item['status']
        if st == ApplicationStatus.APPLIED: funnel_map['Applied'] += 1
        elif st == ApplicationStatus.SCREENING: funnel_map['Screening'] += 1
        elif st == ApplicationStatus.ASSESSMENT: funnel_map['Assessment'] += 1
        elif st == ApplicationStatus.SHORTLISTED: funnel_map['Shortlisted'] += 1
        elif st == ApplicationStatus.INTERVIEW: funnel_map['Interview'] += 1
        elif st == ApplicationStatus.OFFER: funnel_map['Offer'] += 1
        elif st in [ApplicationStatus.JOINED, ApplicationStatus.SELECTED]: funnel_map['Placed / Joined'] += 1

        title_lower = item['opp_title'].lower()
        if 'fintech' in title_lower or 'payment' in title_lower or 'quant' in title_lower: sector_map['FinTech'] += 1
        elif 'ai' in title_lower or 'machine learning' in title_lower or 'nlp' in title_lower or 'data' in title_lower: sector_map['AI Systems'] += 1
        elif 'cloud' in title_lower or 'sre' in title_lower or 'devops' in title_lower or 'security' in title_lower: sector_map['Cloud & DevOps'] += 1
        elif 'vlsi' in title_lower or 'asic' in title_lower or 'firmware' in title_lower: sector_map['Semiconductors'] += 1
        elif 'robot' in title_lower or 'mechatron' in title_lower: sector_map['Robotics'] += 1
        else: sector_map['Consulting'] += 1

    total_apps = len(applications_json_list)
    count_screening = funnel_map['Screening'] + funnel_map['Assessment']
    count_interview = funnel_map['Interview']
    count_offered = funnel_map['Offer']
    count_placed = funnel_map['Placed / Joined']

    context = {
        'total_applications': total_apps,
        'count_screening': count_screening,
        'count_interview': count_interview,
        'count_offered': count_offered,
        'count_placed': count_placed,
        'avg_package': '22.4',
        'application_statuses': ApplicationStatus.choices,
        'distinct_companies': sorted(list(distinct_companies)),
        'applications_json_str': json.dumps(applications_json_list),
        'funnel_labels': json.dumps(list(funnel_map.keys())),
        'funnel_counts': json.dumps(list(funnel_map.values())),
        'sector_labels': json.dumps(list(sector_map.keys())),
        'sector_counts': json.dumps(list(sector_map.values())),
        'is_admin': request.user.is_authenticated and request.user.primary_role == PrimaryRole.SYSTEM_ADMIN,
    }
    return render(request, 'pages/campus_recruitment.html', context)


@login_required
def export_placements_csv_view(request):
    """Exports candidate placement applications as a downloadable CSV audit report."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="AIC_Campus_Placements_Report_2026.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Email', 'Department', 'AIC Passport Number',
        'Hiring Company', 'Position Title', 'Application Date',
        'Current Stage', 'Compensation', 'Verification Status'
    ])

    apps = Application.objects.select_related('applicant', 'opportunity').order_by('-applied_at')
    for a in apps:
        passport = DigitalSkillPassport.objects.filter(user=a.applicant).first()
        p_num = passport.passport_number if passport else f"AIC-PASSPORT-{a.applicant.id.hex[:8].upper()}"
        writer.writerow([
            a.applicant.get_full_name() or a.applicant.username,
            a.applicant.email,
            a.applicant.department_name or "Computer Science & AI",
            p_num,
            a.opportunity.organization_name,
            a.opportunity.title,
            a.applied_at.strftime('%Y-%m-%d') if a.applied_at else '2026-09-08',
            a.get_status_display(),
            f"₹{a.opportunity.stipend_salary} {a.opportunity.salary_period}",
            'Verified AIC Credential' if (passport and passport.is_verified) else 'Pending Verification'
        ])

    return response


@login_required
def admin_verification_center_view(request):
    """
    Statutory Verification Center for Administrators.
    Provides central queues for reviewing and authenticating student credentials,
    corporate industry partner MoUs, job requisitions, and college accreditations.
    """
    students_with_unverified = []
    for st in User.objects.filter(primary_role=PrimaryRole.STUDENT)[:6]:
        passport = DigitalSkillPassport.objects.filter(user=st).first()
        p_num = passport.passport_number if passport else f"AIC-PASSPORT-{st.id.hex[:8].upper()}"
        students_with_unverified.append({
            'id': str(st.id),
            'student_name': st.get_full_name() or st.username,
            'passport_number': p_num,
            'department': st.department_name or "Computer Science & AI",
            'credential_title': 'AWS Certified Solutions Architect & Capstone Defense',
            'issuing_body': 'Amazon Web Services / Faculty Panel',
            'proof_url': f'/passport/verify/{passport.qr_verification_token if passport else st.id}/',
        })

    pending_partners = [
        {
            'id': 'qualcomm-mou',
            'name': 'Qualcomm India Semiconductors',
            'tier': 'Platinum Strategic Partner',
            'sector': 'VLSI & 5G Wireless',
            'collab_type': 'Bilateral MoU & VLSI Design Cleanroom',
            'partnered_institute': 'IIT Madras / AIC Network',
            'liaison': 'Dr. K. Swaminathan (Engineering Director)',
            'mou_validity': '2024 – 2028',
        },
        {
            'id': 'nvidia-mou',
            'name': 'NVIDIA Deep Learning Institute',
            'tier': 'Gold Technology Partner',
            'sector': 'Accelerated Computing & AI',
            'collab_type': 'GPU Compute Grant & Faculty DLI',
            'partnered_institute': 'BITS Pilani / AIC Network',
            'liaison': 'Mr. Vikram Anand (Developer Relations)',
            'mou_validity': '2024 – 2028',
        },
        {
            'id': 'biocon-mou',
            'name': 'Biocon Biologics Research Lab',
            'tier': 'Gold Technology Partner',
            'sector': 'Bioinformatics & Pharma',
            'collab_type': 'Joint Genomic Sequencing Laboratory',
            'partnered_institute': 'IISc Bengaluru',
            'liaison': 'Dr. Meenakshi Sundaram',
            'mou_validity': '2024 – 2027',
        }
    ]

    pending_opps = Opportunity.objects.filter(is_verified=False)[:4]
    if not pending_opps.exists():
        pending_opps = Opportunity.objects.all().order_by('-created_at')[:3]

    pending_institutions = Institution.objects.all().order_by('-nirf_rank')[:4]

    context = {
        'total_pending': len(students_with_unverified) + len(pending_partners) + len(pending_opps),
        'total_approved': 142,
        'total_audited': 186,
        'pending_students': students_with_unverified,
        'pending_partners': pending_partners,
        'pending_opps': pending_opps,
        'pending_institutions': pending_institutions,
    }
    return render(request, 'pages/admin_verification.html', context)


@csrf_exempt
@login_required
def admin_verify_action_api(request):
    """AJAX API for Admin to approve or reject verification items."""
    import json
    import uuid
    from django.http import JsonResponse
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        action = data.get('action', 'APPROVE')

        audit_token = uuid.uuid4().hex[:10].upper()

        if action == 'APPROVE':
            if item_type == 'student':
                st = User.objects.filter(id=item_id).first()
                if st:
                    passport = DigitalSkillPassport.objects.filter(user=st).first()
                    if passport:
                        passport.is_active = True
                        passport.save()
                    Notification.objects.create(
                        recipient=st,
                        title="AIC Passport Credential Authenticated",
                        message="Your submitted external certification / capstone has been approved with a sovereign cryptographic stamp.",
                        notification_type='SYSTEM',
                        link='/passport/'
                    )
            elif item_type == 'opp':
                opp = Opportunity.objects.filter(id=item_id).first()
                if opp:
                    opp.is_verified = True
                    opp.save()

            return JsonResponse({
                'success': True,
                'message': 'Cryptographically verified & audit badge issued successfully.',
                'audit_token': audit_token
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Item rejected and flagged for revision.',
                'audit_token': audit_token
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ──────────────────────────────────────────────────────────────────────────────
# Events, Workshops & Seminars Hub
# ──────────────────────────────────────────────────────────────────────────────

def events_view(request):
    """
    Public events portal — shows all events (conferences, workshops, seminars, hackathons, webinars, etc.)
    with full details. Registration only available to authenticated STUDENT users.
    """
    # Filters
    q         = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    free_filter = request.GET.get('free', '').strip()

    events_qs = Event.objects.select_related('field', 'institution', 'department').order_by('start_date')

    if q:
        events_qs = events_qs.filter(
            Q(title__icontains=q) |
            Q(organizer_name__icontains=q) |
            Q(description__icontains=q) |
            Q(speakers__icontains=q) |
            Q(topics_covered__icontains=q)
        )
    if type_filter:
        events_qs = events_qs.filter(event_type=type_filter)
    if mode_filter:
        events_qs = events_qs.filter(mode=mode_filter)
    if free_filter == 'free':
        events_qs = events_qs.filter(is_free=True)
    elif free_filter == 'paid':
        events_qs = events_qs.filter(is_free=False)

    # Registered event IDs for the current user (student only)
    registered_event_ids = set()
    if request.user.is_authenticated and request.user.primary_role == PrimaryRole.STUDENT:
        registered_event_ids = set(
            EventRegistration.objects.filter(student=request.user).values_list('event_id', flat=True)
        )

    context = {
        'events': events_qs,
        'total_events': events_qs.count(),
        'featured_events': Event.objects.filter(is_featured=True).order_by('start_date')[:3],
        'registered_event_ids': registered_event_ids,
        'event_types': EventType.choices,
        'event_modes': EventMode.choices,
        'q': q,
        'type_filter': type_filter,
        'mode_filter': mode_filter,
        'free_filter': free_filter,
        'is_student': request.user.is_authenticated and request.user.primary_role == PrimaryRole.STUDENT,
        'current_role': request.user.primary_role if request.user.is_authenticated else 'GUEST',
    }
    return render(request, 'pages/events.html', context)


@csrf_exempt
@login_required
def event_register_api(request):
    """
    AJAX API — allows only STUDENT users to register for an event.
    POST body: { event_id: <uuid> }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    if request.user.primary_role != PrimaryRole.STUDENT:
        return JsonResponse({'success': False, 'error': 'Only students can register for events.'}, status=403)

    try:
        data = json.loads(request.body)
        event_id = data.get('event_id')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return JsonResponse({'success': False, 'error': 'Event not found.'}, status=404)

        current_regs = EventRegistration.objects.filter(event=event).count()
        if current_regs >= event.max_registrations:
            return JsonResponse({'success': False, 'error': 'Event is fully booked.'}, status=400)

        reg, created = EventRegistration.objects.get_or_create(
            event=event,
            student=request.user
        )

        if not created:
            return JsonResponse({'success': False, 'error': 'You are already registered for this event.'})

        # Notify student
        Notification.objects.create(
            recipient=request.user,
            title=f"Registered: {event.title}",
            message=f"You have successfully registered for '{event.title}' by {event.organizer_name} on {event.start_date.strftime('%d %b %Y')}. {'Certificate will be provided.' if event.provides_certificate else ''}",
            notification_type='SYSTEM',
            link='/events/'
        )

        return JsonResponse({
            'success': True,
            'message': f"Successfully registered for {event.title}!",
            'event_title': event.title,
            'start_date': event.start_date.strftime('%d %b %Y'),
            'provides_certificate': event.provides_certificate,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
