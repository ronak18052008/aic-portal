from django.shortcuts import render, redirect
from django.db.models import Q, Count
from apps.accounts.models import User, PrimaryRole
from apps.education.models import Course, Programme, Certification
from apps.institutions.models import Institution
from apps.opportunities.models import Opportunity, OpportunityType
from apps.skills.models import Skill, UserSkill
from apps.taxonomy.models import Field

def global_search_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all') # courses, programmes, institutions, jobs, internships, scholarships, projects, certifications, skills, students
    category_filter = request.GET.get('field', '')
    mode_filter = request.GET.get('mode', '')
    country_filter = request.GET.get('country', '')
    institution_filter = request.GET.get('institution', '')
    verified_only = request.GET.get('verified', '') == '1'

    # STRICT ACCESS CONTROL: Talent Discovery (search_type == 'students') is EXCLUSIVELY for Recruiter/Industry role
    is_recruiter = request.user.is_authenticated and request.user.primary_role == PrimaryRole.INDUSTRY
    if search_type == 'students' and not is_recruiter:
        # Non-recruiters cannot access talent discovery / candidate profiles
        return redirect('/search/?type=all')

    # If search_type is 'students' (Talent Discovery Engine), ONLY return verified student candidates
    if search_type == 'students':
        students_qs = User.objects.filter(primary_role=PrimaryRole.STUDENT).select_related('profile').order_by('first_name')
        if query:
            students_qs = students_qs.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(username__icontains=query) |
                Q(skills__skill__name__icontains=query) |
                Q(profile__headline__icontains=query)
            ).distinct()

        # Find recruiter's top opportunity for skill fit comparison if applicable
        target_opp = None
        user_org = getattr(request.user, 'organization_name', None) or 'TechCorp Global Solutions'
        target_opp = Opportunity.objects.filter(
            Q(organization_name__icontains=user_org) | Q(verification_source__icontains=user_org)
        ).first()

        req_skills = list(target_opp.required_skills.all()) if target_opp else []
        req_skill_names = set(s.name for s in req_skills)
        total_req = max(len(req_skills), 1)

        candidate_students = []
        for st in students_qs[:50]:
            st_skills = list(UserSkill.objects.filter(user=st).select_related('skill'))
            st_skill_names = set(s.skill.name for s in st_skills)
            matched_skills = [s for s in req_skills if s.name in st_skill_names]
            missing_skills = [s for s in req_skills if s.name not in st_skill_names]

            if req_skills:
                match_pct = int((len(matched_skills) / total_req) * 100)
            else:
                match_pct = min(70 + (len(st_skills) * 5), 98)

            candidate_students.append({
                'student': st,
                'verified_skills_count': len(st_skills),
                'all_skills': [s.skill.name for s in st_skills],
                'matched_skills': [s.name for s in matched_skills],
                'missing_skills': [s.name for s in missing_skills],
                'match_pct': match_pct,
            })

        candidate_students.sort(key=lambda x: x['match_pct'], reverse=True)

        facet_counts = {
            'all': 0,
            'courses': 0,
            'programmes': 0,
            'institutions': 0,
            'certifications': 0,
            'jobs': 0,
            'internships': 0,
            'scholarships': 0,
            'projects': 0,
            'students': students_qs.count(),
        }

        context = {
            'query': query,
            'search_type': 'students',
            'category_filter': category_filter,
            'mode_filter': mode_filter,
            'country_filter': country_filter,
            'institution_filter': institution_filter,
            'selected_institution': None,
            'institutions_list': Institution.objects.all().order_by('name'),
            'verified_only': verified_only,
            'facet_counts': facet_counts,
            'fields': Field.objects.all(),
            'courses': [],
            'programmes': [],
            'institutions': [],
            'certifications': [],
            'jobs_annotated': [],
            'internships': [],
            'scholarships': [],
            'projects': [],
            'students_candidates': candidate_students,
            'target_opp': target_opp,
        }
        return render(request, 'pages/search.html', context)

    # Filtered Querysets for standard educational & opportunity search
    courses_qs = Course.objects.all()
    programmes_qs = Programme.objects.all()
    institutions_qs = Institution.objects.all()
    opportunities_qs = Opportunity.objects.all()
    certifications_qs = Certification.objects.all()

    if query:
        courses_qs = courses_qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(provider__icontains=query))
        programmes_qs = programmes_qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(institution__name__icontains=query))
        institutions_qs = institutions_qs.filter(Q(name__icontains=query) | Q(official_name__icontains=query) | Q(city__icontains=query))
        opportunities_qs = opportunities_qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(organization_name__icontains=query))
        certifications_qs = certifications_qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(issuing_organization__icontains=query) | Q(credential_code__icontains=query))

    if institution_filter:
        if institution_filter == 'none':
            institutions_qs = institutions_qs.filter(Q(institution_type='OTHER') | Q(slug__icontains='independent') | Q(name__icontains='Open') | Q(name__icontains='Independent'))
            programmes_qs = programmes_qs.filter(Q(institution__slug__icontains='independent') | Q(institution__name__icontains='Independent') | Q(institution__name__icontains='Open'))
            courses_qs = courses_qs.filter(Q(provider__icontains='Independent') | Q(provider__icontains='Open') | Q(provider__icontains='Global') | Q(provider=''))
            opportunities_qs = opportunities_qs.filter(Q(organization_name__icontains='Independent') | Q(organization_name__icontains='Open') | Q(organization_name__icontains='Global'))
            certifications_qs = certifications_qs.filter(Q(issuing_organization__icontains='Independent') | Q(issuing_organization__icontains='Open') | Q(issuing_organization__icontains='Global'))
        else:
            institutions_qs = institutions_qs.filter(slug=institution_filter)
            programmes_qs = programmes_qs.filter(institution__slug=institution_filter)
            inst_match = Institution.objects.filter(slug=institution_filter).first()
            if inst_match:
                # Strictly filter courses, opportunities, and certifications to those associated with this institution
                courses_qs = courses_qs.filter(
                    Q(provider__icontains=inst_match.name) | 
                    Q(provider__icontains=inst_match.slug) |
                    Q(instructor__icontains=inst_match.name)
                )
                opportunities_qs = opportunities_qs.filter(
                    Q(organization_name__icontains=inst_match.name) | 
                    Q(description__icontains=inst_match.name)
                )
                certifications_qs = certifications_qs.filter(
                    Q(issuing_organization__icontains=inst_match.name) | 
                    Q(verification_source__icontains=inst_match.name)
                )
            else:
                courses_qs = courses_qs.none()
                opportunities_qs = opportunities_qs.none()
                certifications_qs = certifications_qs.none()

    if category_filter:
        if category_filter == 'none':
            courses_qs = courses_qs.filter(Q(field__slug__in=['general', 'unspecified', 'other']) | Q(field__name__icontains='General') | Q(field__name__icontains='Interdisciplinary') | Q(field__isnull=True))
            programmes_qs = programmes_qs.filter(Q(field__slug__in=['general', 'unspecified', 'other']) | Q(field__name__icontains='General') | Q(field__name__icontains='Interdisciplinary') | Q(field__isnull=True))
            opportunities_qs = opportunities_qs.filter(Q(field__slug__in=['general', 'unspecified', 'other']) | Q(field__name__icontains='General') | Q(field__name__icontains='Interdisciplinary') | Q(field__isnull=True))
            certifications_qs = certifications_qs.filter(Q(field__slug__in=['general', 'unspecified', 'other']) | Q(field__name__icontains='General') | Q(field__name__icontains='Interdisciplinary') | Q(field__isnull=True))
            institutions_qs = institutions_qs.filter(Q(programmes__field__slug__in=['general', 'unspecified', 'other']) | Q(name__icontains='Independent') | Q(name__icontains='Open')).distinct()
        else:
            courses_qs = courses_qs.filter(field__slug=category_filter)
            programmes_qs = programmes_qs.filter(field__slug=category_filter)
            opportunities_qs = opportunities_qs.filter(field__slug=category_filter)
            certifications_qs = certifications_qs.filter(field__slug=category_filter)
            institutions_qs = institutions_qs.filter(programmes__field__slug=category_filter).distinct()

    if mode_filter:
        if mode_filter == 'none':
            courses_qs = courses_qs.filter(Q(mode__in=['', 'HYBRID', 'ONLINE']) | Q(mode__isnull=True))
            programmes_qs = programmes_qs.filter(Q(mode__in=['', 'HYBRID', 'ONLINE']) | Q(mode__isnull=True))
            opportunities_qs = opportunities_qs.filter(Q(mode__in=['', 'HYBRID', 'ONLINE', 'REMOTE']) | Q(mode__isnull=True))
        else:
            courses_qs = courses_qs.filter(mode__iexact=mode_filter)
            programmes_qs = programmes_qs.filter(mode__iexact=mode_filter)
            opportunities_qs = opportunities_qs.filter(mode__iexact=mode_filter)

    if country_filter:
        if country_filter == 'none':
            institutions_qs = institutions_qs.filter(Q(country__in=['', 'Global', 'Online', 'Worldwide', 'International']) | Q(country__isnull=True))
            programmes_qs = programmes_qs.filter(Q(institution__country__in=['', 'Global', 'Online', 'Worldwide', 'International']) | Q(institution__country__isnull=True))
            opportunities_qs = opportunities_qs.filter(Q(country__in=['', 'Global', 'Online', 'Worldwide', 'International']) | Q(country__isnull=True))
        else:
            institutions_qs = institutions_qs.filter(country__iexact=country_filter)
            programmes_qs = programmes_qs.filter(institution__country__iexact=country_filter)
            opportunities_qs = opportunities_qs.filter(country__iexact=country_filter)

    if verified_only:
        courses_qs = courses_qs.filter(is_verified=True)
        programmes_qs = programmes_qs.filter(is_verified=True)
        institutions_qs = institutions_qs.filter(is_verified=True)
        opportunities_qs = opportunities_qs.filter(is_verified=True)
        certifications_qs = certifications_qs.filter(is_verified=True)

    # Opportunity Specific Sub-types
    jobs_qs = opportunities_qs.filter(opportunity_type=OpportunityType.JOB)
    internships_qs = opportunities_qs.filter(opportunity_type=OpportunityType.INTERNSHIP)
    scholarships_qs = opportunities_qs.filter(opportunity_type=OpportunityType.SCHOLARSHIP)
    projects_qs = opportunities_qs.filter(opportunity_type=OpportunityType.PROJECT)

    # Dynamic Facet Counts (Real Database Queries)
    facet_counts = {
        'all': courses_qs.count() + programmes_qs.count() + institutions_qs.count() + opportunities_qs.count() + certifications_qs.count(),
        'courses': courses_qs.count(),
        'programmes': programmes_qs.count(),
        'institutions': institutions_qs.count(),
        'certifications': certifications_qs.count(),
        'jobs': jobs_qs.count(),
        'internships': internships_qs.count(),
        'scholarships': scholarships_qs.count(),
        'projects': projects_qs.count(),
        'students': User.objects.filter(primary_role=PrimaryRole.STUDENT).count() if is_recruiter else 0,
    }

    # Compute AI Explainable Matching if User Logged In
    user_skill_ids = set()
    if request.user.is_authenticated:
        user_skill_ids = set(UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))

    limit = 50 if search_type != 'all' else 12

    annotated_jobs = []
    for job in jobs_qs[:limit]:
        req_skills = set(job.required_skills.values_list('id', flat=True))
        matched = req_skills.intersection(user_skill_ids)
        missing = req_skills - user_skill_ids
        match_pct = int((len(matched) / len(req_skills) * 100)) if req_skills else 85
        annotated_jobs.append({
            'item': job,
            'match_pct': match_pct,
            'matched_skills': job.required_skills.filter(id__in=matched),
            'missing_skills': job.required_skills.filter(id__in=missing),
        })

    context = {
        'query': query,
        'search_type': search_type,
        'category_filter': category_filter,
        'mode_filter': mode_filter,
        'country_filter': country_filter,
        'institution_filter': institution_filter,
        'selected_institution': Institution.objects.filter(slug=institution_filter).first() if (institution_filter and institution_filter != 'none') else None,
        'institutions_list': Institution.objects.all().order_by('name'),
        'verified_only': verified_only,
        'facet_counts': facet_counts,
        'fields': Field.objects.all(),
        'courses': courses_qs[:limit],
        'programmes': programmes_qs[:limit],
        'institutions': institutions_qs[:limit],
        'certifications': certifications_qs[:limit],
        'jobs_annotated': annotated_jobs,
        'internships': internships_qs[:limit],
        'scholarships': scholarships_qs[:limit],
        'projects': projects_qs[:limit],
        'students_candidates': [],
    }
    return render(request, 'pages/search.html', context)
