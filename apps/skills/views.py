import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg

from apps.skills.models import Skill, UserSkill, SkillProficiency, SkillEvidence, Assessment, Question, DigitalSkillPassport
from apps.education.models import Course, Certification
from apps.opportunities.models import Opportunity
from apps.taxonomy.models import Field
from apps.accounts.models import User, PrimaryRole
from apps.notifications.models import Notification

@login_required
def skills_overview_view(request):
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill', 'skill__field')
    user_skill_ids = set(user_skills.values_list('skill_id', flat=True))
    available_skills = Skill.objects.exclude(id__in=user_skill_ids).select_related('field')

    # Build cascading mapping: Field ID -> List of Skills
    fields_with_skills = []
    fields = Field.objects.all().order_by('name')
    for f in fields:
        field_sk_list = [
            {'id': str(sk.id), 'name': sk.name, 'category': sk.category}
            for sk in available_skills if sk.field_id == f.id
        ]
        if field_sk_list:
            fields_with_skills.append({
                'id': str(f.id),
                'name': f.name,
                'skills': field_sk_list
            })

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        proficiency = request.POST.get('proficiency', SkillProficiency.INTERMEDIATE)
        if skill_id:
            try:
                skill = Skill.objects.get(id=skill_id)
                UserSkill.objects.update_or_create(
                    user=request.user,
                    skill=skill,
                    defaults={
                        'proficiency': proficiency,
                        'evidence_type': SkillEvidence.SELF_DECLARED,
                        'score_percentage': 75
                    }
                )
            except Skill.DoesNotExist:
                pass
            return redirect('skills_overview')

    return render(request, 'pages/skills_overview.html', {
        'user_skills': user_skills,
        'available_skills': available_skills,
        'fields_with_skills': fields_with_skills,
        'fields_with_skills_json': json.dumps(fields_with_skills),
        'proficiency_choices': SkillProficiency.choices,
    })

@csrf_exempt
@login_required
def submit_assessment_api(request):
    """
    Handles submission of adaptive skill assessment answers.
    Evaluates MCQ answers, computes percentage score, updates UserSkill,
    verifies AIC Passport, creates an in-app Notification,
    and returns score report with explanation for each question.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        assessment_id = data.get('assessment_id')
        answers = data.get('answers', {}) # Dict of {question_id: selected_option}

        assessment = get_object_or_404(Assessment, id=assessment_id)
        questions = assessment.questions.all()
        total_q = questions.count()

        if total_q == 0:
            return JsonResponse({'success': False, 'error': 'No questions found for this assessment.'}, status=400)

        correct_count = 0
        review_details = []

        for q in questions:
            qid_str = str(q.id)
            user_opt = answers.get(qid_str, '').upper()
            is_correct = (user_opt == q.correct_option)
            if is_correct:
                correct_count += 1

            review_details.append({
                'question_id': qid_str,
                'question_text': q.question_text,
                'user_option': user_opt,
                'correct_option': q.correct_option,
                'is_correct': is_correct,
                'explanation': q.explanation or f"The correct answer is Option {q.correct_option}."
            })

        score_percentage = int((correct_count / total_q) * 100)
        passed = score_percentage >= assessment.pass_mark

        # Determine Proficiency Level based on score
        if score_percentage >= 90:
            prof_level = SkillProficiency.EXPERT
        elif score_percentage >= 75:
            prof_level = SkillProficiency.ADVANCED
        elif score_percentage >= 60:
            prof_level = SkillProficiency.INTERMEDIATE
        else:
            prof_level = SkillProficiency.ELEMENTARY

        # Update or Create verified UserSkill
        user_skill, _ = UserSkill.objects.update_or_create(
            user=request.user,
            skill=assessment.skill,
            defaults={
                'proficiency': prof_level,
                'evidence_type': SkillEvidence.ASSESSMENT,
                'score_percentage': score_percentage,
                'verified_by': f"AIC Adaptive Engine ({assessment.title})"
            }
        )

        # Ensure DigitalSkillPassport exists and mark verified
        passport, _ = DigitalSkillPassport.objects.get_or_create(
            user=request.user,
            defaults={'passport_number': f"AIC-PASSPORT-{request.user.id.hex[:8].upper()}"}
        )
        passport.is_verified = True
        passport.save()

        # Send Notification to user
        Notification.objects.create(
            recipient=request.user,
            title=f"Assessment Completed: {assessment.skill.name}",
            message=f"You scored {score_percentage}% on the {assessment.title}. Your verified badge is now active on your AIC Passport and Resume!",
            notification_type='ASSESSMENT',
            link='/passport/'
        )

        return JsonResponse({
            'success': True,
            'assessment_title': assessment.title,
            'skill_name': assessment.skill.name,
            'total_questions': total_q,
            'correct_count': correct_count,
            'score_percentage': score_percentage,
            'pass_mark': assessment.pass_mark,
            'passed': passed,
            'proficiency_awarded': prof_level,
            'review_details': review_details,
            'passport_url': '/passport/',
            'resume_url': '/resume/builder/'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def skill_gap_view(request):
    """
    Intelligent Skill Gap & Career Target Analysis Engine.
    - If user is ACADEMICIAN: displays Institutional Student Cohort Skill Gap Analysis,
      cohort readiness, critical curriculum deficits, and interventions.
    - If user is STUDENT (or other): maps all 20 taxonomy fields to industry career targets
      with matched vs missing skills, career readiness / gap percentages, and targeted recommendations.
    """
    # -------------------------------------------------------------------------
    # 1. ACADEMICIAN / INSTITUTION / ADMIN VIEW: Student Cohort Skill Gap Engine
    # -------------------------------------------------------------------------
    if request.user.primary_role in [PrimaryRole.ACADEMICIAN, PrimaryRole.INSTITUTION, PrimaryRole.SYSTEM_ADMIN]:
        cohort_students = User.objects.filter(primary_role=PrimaryRole.STUDENT).order_by('first_name', 'last_name')
        total_students_cohort = cohort_students.count()

        cohort_skills = UserSkill.objects.filter(user__in=cohort_students).select_related('skill', 'skill__field')
        
        # Most acquired skills in cohort
        top_cohort_skills = cohort_skills.values('skill__name', 'skill__category', 'skill__field__name').annotate(
            student_count=Count('id'),
            avg_score=Avg('score_percentage')
        ).order_by('-student_count')[:8]

        # Critical Skill Deficits (High-demand industry skills with low student enrollment)
        high_demand_skills = Skill.objects.all().order_by('-industry_demand_score')

        deficit_skills = []
        for sk in high_demand_skills:
            acquired_by = cohort_skills.filter(skill=sk).count()
            acquisition_rate = int((acquired_by / max(total_students_cohort, 1)) * 100)
            if acquisition_rate < 50:
                deficit_skills.append({
                    'skill': sk,
                    'acquired_by': acquired_by,
                    'deficit_rate': 100 - acquisition_rate,
                    'demand_score': sk.industry_demand_score
                })
            if len(deficit_skills) >= 6:
                break

        # Faculty Curriculum Interventions / Recommended FDPs
        recommended_fdp_courses = Course.objects.filter(level_name__in=['Advanced Faculty', 'Professional Educator', 'Specialty Educator'])[:4]

        # Cohort readiness average
        avg_cohort_score = cohort_skills.aggregate(Avg('score_percentage'))['score_percentage__avg'] or 78.5

        # Individual Student Skill Gap Profile Computation
        DEFAULT_ROLES_PER_FIELD = {
            'computer-science': ('AI & Machine Learning Systems Architect', ['Python Programming', 'PyTorch Deep Learning', 'Large Language Models (LLMs)', 'Machine Learning Algorithms', 'FastAPI Microservices']),
            'data-science': ('Lead Data Scientist', ['Python Programming', 'Pandas & NumPy Numerical Computing', 'Scikit-Learn Machine Learning', 'SQL Advanced Query Optimization', 'MLflow Machine Learning Lifecycle']),
            'cybersecurity-cloud': ('Cloud Solutions Architect (AWS / Multi-Cloud)', ['AWS Cloud Architecture', 'Docker Containerization', 'Kubernetes Orchestration', 'Terraform Infrastructure as Code', 'Linux Kernel & Shell Scripting']),
            'vlsi-semiconductors': ('Digital ASIC / RTL Design Engineer', ['VLSI Chip Design & Verilog', 'SystemVerilog Verification', 'FPGA Prototyping', 'Embedded C & Microcontrollers']),
            'business-fintech': ('Quantitative Finance & Algorithmic Trader', ['Algorithmic Trading & Quantitative Finance', 'Financial Modeling & Valuation', 'Python Programming', 'SQL Advanced Query Optimization']),
            'design-uiux': ('Lead Product & UX Systems Designer', ['UI Design & Figma Prototyping', 'UX Research & User Testing', 'Product Design & Design Systems', 'React.js Frontend Architecture']),
        }

        # Role assignment rotation for students based on their skills
        student_gap_list = []
        students_json_list = []

        for idx, student in enumerate(cohort_students):
            st_skills = list(UserSkill.objects.filter(user=student).select_related('skill', 'skill__field'))
            st_skill_names = [s.skill.name for s in st_skills]
            st_skill_set = set(st_skill_names)

            # Determine target role based on student's skills or indexed field
            if any('UI' in s or 'Design' in s for s in st_skill_names):
                target_role, req_skills = DEFAULT_ROLES_PER_FIELD['design-uiux']
                field_label = 'UI/UX & Design'
            elif any('Pandas' in s or 'Data' in s for s in st_skill_names):
                target_role, req_skills = DEFAULT_ROLES_PER_FIELD['data-science']
                field_label = 'Data Science & AI'
            elif any('Linux' in s or 'Kubernetes' in s for s in st_skill_names):
                target_role, req_skills = DEFAULT_ROLES_PER_FIELD['cybersecurity-cloud']
                field_label = 'Cybersecurity & Cloud'
            else:
                target_role, req_skills = DEFAULT_ROLES_PER_FIELD['computer-science']
                field_label = 'Computer Science & AI'

            matched = [s for s in req_skills if s in st_skill_set]
            missing = [s for s in req_skills if s not in st_skill_set]
            total_req = max(len(req_skills), 1)
            match_pct = int((len(matched) / total_req) * 100)
            gap_pct = max(100 - match_pct, 0)

            # Recommended courses for missing skills
            sample_course = Course.objects.filter(field__name__icontains=field_label.split()[0]).first()
            rec_course_title = sample_course.title if sample_course else f"Comprehensive {field_label} Mastery"
            rec_course_provider = sample_course.provider if sample_course else "AIC Skill Portal"

            passport = DigitalSkillPassport.objects.filter(user=student).first()
            passport_num = passport.passport_number if passport else f"AIC-PASSPORT-{student.id.hex[:8].upper()}"

            student_data = {
                'id': str(student.id),
                'name': student.get_full_name() or student.username or student.email.split('@')[0].capitalize(),
                'email': student.email,
                'department': student.department_name or field_label,
                'passport_number': passport_num,
                'target_role': target_role,
                'field_label': field_label,
                'verified_count': len(st_skills),
                'verified_skill_names': st_skill_names,
                'match_pct': match_pct,
                'gap_pct': gap_pct,
                'readiness_score': min(max(match_pct + 12, 45), 98),
                'matched_skills': matched,
                'missing_skills': missing,
                'rec_course_title': rec_course_title,
                'rec_course_provider': rec_course_provider,
            }
            student_gap_list.append(student_data)
            students_json_list.append(student_data)

        # Graphical Data for Charts
        chart_deficit_labels = [ds['skill'].name for ds in deficit_skills]
        chart_deficit_demand = [ds['demand_score'] for ds in deficit_skills]
        chart_cohort_coverage = [100 - ds['deficit_rate'] for ds in deficit_skills]

        high_readiness = sum(1 for s in student_gap_list if s['match_pct'] >= 70)
        mod_readiness = sum(1 for s in student_gap_list if 40 <= s['match_pct'] < 70)
        low_readiness = sum(1 for s in student_gap_list if s['match_pct'] < 40)

        context = {
            'is_faculty_view': True,
            'is_admin_or_institution': request.user.primary_role in [PrimaryRole.INSTITUTION, PrimaryRole.SYSTEM_ADMIN],
            'total_students_cohort': total_students_cohort,
            'total_verified_credentials': cohort_skills.count(),
            'avg_cohort_score': round(avg_cohort_score, 1),
            'top_cohort_skills': top_cohort_skills,
            'deficit_skills': deficit_skills,
            'recommended_fdp_courses': recommended_fdp_courses,
            'student_gap_list': student_gap_list,
            'students_json_str': json.dumps(students_json_list),
            'chart_deficit_labels': json.dumps(chart_deficit_labels),
            'chart_deficit_demand': json.dumps(chart_deficit_demand),
            'chart_cohort_coverage': json.dumps(chart_cohort_coverage),
            'chart_readiness_counts': json.dumps([high_readiness, mod_readiness, low_readiness]),
        }
        return render(request, 'pages/skill_gap.html', context)

    # -------------------------------------------------------------
    # 2. STUDENT VIEW: Personal Career Role Skill Gap Analysis
    # -------------------------------------------------------------
    user_skills_qs = UserSkill.objects.filter(user=request.user).select_related('skill', 'skill__field')
    user_skill_ids = set(user_skills_qs.values_list('skill_id', flat=True))
    user_skill_names = set(user_skills_qs.values_list('skill__name', flat=True))

    FIELD_CAREER_MAP = {
        'computer-science': {
            'field_name': 'Computer Science & AI',
            'roles': {
                'AI & Machine Learning Systems Architect': ['Python Programming', 'PyTorch Deep Learning', 'Large Language Models (LLMs)', 'Machine Learning Algorithms', 'FastAPI Microservices'],
                'Full Stack Cloud & Web Engineer': ['Python Programming', 'Django Web Framework', 'React.js Frontend Architecture', 'PostgreSQL Database Architect', 'TypeScript Engineering'],
                'Systems & Low-Level Infrastructure Engineer': ['C++ Systems Programming', 'Rust Systems Language', 'Linux Kernel & Shell Scripting', 'Docker Containerization'],
                'Mobile App Architect (Flutter & Android)': ['Flutter Cross-Platform Mobile', 'Kotlin Android Modern Development', 'RESTful API Design & GraphQL', 'Firebase Realtime Architecture'],
                'LLM & GenAI Applications Specialist': ['Large Language Models (LLMs)', 'LangChain & LlamaIndex Frameworks', 'Hugging Face Transformers Library', 'Vector Databases (Chroma, Pinecone, Milvus)', 'LLMOps & Foundation Model Fine-Tuning'],
            }
        },
        'data-science': {
            'field_name': 'Data Science & Analytics',
            'roles': {
                'Lead Data Scientist': ['Python Programming', 'Pandas & NumPy Numerical Computing', 'Scikit-Learn Machine Learning', 'SQL Advanced Query Optimization', 'MLflow Machine Learning Lifecycle'],
                'Big Data & Lakehouse Platform Engineer': ['Apache Spark & Distributed Computing', 'Apache Kafka Streaming', 'Apache Airflow Workflow Orchestration', 'Databricks Lakehouse Platform', 'Data Warehouse Design (Snowflake/BigQuery)'],
                'Business Intelligence & Analytics Specialist': ['SQL Advanced Query Optimization', 'PowerBI Analytics & Dashboards', 'Tableau Data Visualization', 'dbt (data build tool) Transformations'],
            }
        },
        'cybersecurity-cloud': {
            'field_name': 'Cybersecurity & Cloud',
            'roles': {
                'Cloud Solutions Architect (AWS / Multi-Cloud)': ['AWS Cloud Architecture', 'Docker Containerization', 'Kubernetes Orchestration', 'Terraform Infrastructure as Code', 'Linux Kernel & Shell Scripting'],
                'Information Security & Ethical Hacker': ['Ethical Hacking & Penetration Testing', 'Network Security & Firewalls', 'Linux Kernel & Shell Scripting', 'Cloud Security Engineering'],
                'DevSecOps & Site Reliability Engineer (SRE)': ['Ansible Configuration Management', 'Prometheus & Grafana Observability', 'Docker Containerization', 'Kubernetes Orchestration', 'Terraform Infrastructure as Code'],
            }
        },
        'vlsi-semiconductors': {
            'field_name': 'VLSI & Microelectronics',
            'roles': {
                'Digital ASIC / RTL Design Engineer': ['VLSI Chip Design & Verilog', 'SystemVerilog Verification', 'FPGA Prototyping', 'Embedded C & Microcontrollers'],
                'Embedded Systems & Firmware Engineer': ['Embedded C & Microcontrollers', 'FPGA Prototyping', 'C++ Systems Programming', 'Linux Kernel & Shell Scripting'],
            }
        },
        'business-fintech': {
            'field_name': 'Business & FinTech',
            'roles': {
                'Quantitative Finance & Algorithmic Trader': ['Algorithmic Trading & Quantitative Finance', 'Financial Modeling & Valuation', 'Python Programming', 'SQL Advanced Query Optimization'],
                'Web3 & Smart Contract Developer': ['Blockchain & Smart Contracts (Solidity)', 'Solidity Smart Contract Development', 'TypeScript Engineering', 'Docker Containerization'],
            }
        },
        'robotics-mechatronics': {
            'field_name': 'Robotics & Automation',
            'roles': {
                'Autonomous Robotics Systems Engineer': ['Robot Operating System (ROS 2)', 'Autonomous Drone Navigation', 'MATLAB & Simulink Dynamics', 'C++ Systems Programming'],
            }
        },
        'design-uiux': {
            'field_name': 'UI/UX & Product Design',
            'roles': {
                'Lead Product & UX Systems Designer': ['UI Design & Figma Prototyping', 'UX Research & User Testing', 'Product Design & Design Systems', 'React.js Frontend Architecture'],
            }
        },
        'biomedical-health': {
            'field_name': 'Biomedical & Medical AI',
            'roles': {
                'Biomedical AI & Diagnostic Specialist': ['Biomedical Signal Processing', 'Medical Image Segmentation (DICOM)', 'Python Programming', 'PyTorch Deep Learning'],
            }
        },
        'environment-climate': {
            'field_name': 'Climate Tech & Renewable Energy',
            'roles': {
                'Renewable Energy & Smart Grid Systems Analyst': ['Solar PV System Design', 'Wind Turbine Aerodynamics', 'Smart Grid Power Systems', 'GIS Spatial Climate Mapping'],
            }
        },
        'agriculture-food': {
            'field_name': 'AgTech & Food Security',
            'roles': {
                'Precision Agriculture & Crop AI Specialist': ['Precision Agriculture Drone Mapping', 'Hydroponics & Controlled Environment Farming', 'Soil Microbiology & Chemistry', 'Python Programming'],
            }
        },
        'aerospace-defence': {
            'field_name': 'Aerospace & Defence Systems',
            'roles': {
                'Aerospace Flight Dynamics & Avionics Engineer': ['Computational Fluid Dynamics (OpenFOAM)', 'Avionics Bus Protocols (MIL-STD-1553)', 'Orbital Mechanics & Astrodynamics', 'Embedded C & Microcontrollers'],
            }
        },
        'physics-quantum': {
            'field_name': 'Quantum Computing & Advanced Physics',
            'roles': {
                'Quantum Software & Circuit Engineer': ['Qiskit Quantum Circuit Design', 'Quantum Algorithm Development', 'Python Programming', 'C++ Systems Programming'],
            }
        },
        'chemical-materials': {
            'field_name': 'Chemical Engineering & Nanotech',
            'roles': {
                'Molecular Simulation & Materials Chemist': ['Chemical Process Simulation (Aspen Plus)', 'Molecular Dynamics (GROMACS/LAMMPS)', 'Polymer Synthesis & Nanomaterials', 'Python Programming'],
            }
        },
        'civil-smart-cities': {
            'field_name': 'Smart Cities & Infrastructure',
            'roles': {
                'Smart Urban Infrastructure & BIM Lead': ['Building Information Modeling (BIM/Revit)', 'Structural Health Monitoring Sensors', 'GIS Spatial Climate Mapping', 'Python Programming'],
            }
        },
        'genetics-biotech': {
            'field_name': 'Genomics & Synthetic Biology',
            'roles': {
                'Computational Genomics & CRISPR Specialist': ['CRISPR-Cas9 Gene Editing Protocols', 'Bioinformatics Pipeline (Nextflow/Snakemake)', 'Next-Generation Sequencing (NGS) Analysis', 'Python Programming'],
            }
        },
        'neuroscience-cog': {
            'field_name': 'Cognitive Science & Neurotechnology',
            'roles': {
                'Brain-Computer Interface (BCI) Engineer': ['EEG Signal Processing & BCI Systems', 'Computational Neuroscience Modeling', 'Python Programming', 'PyTorch Deep Learning'],
            }
        },
        'legal-governance': {
            'field_name': 'AI Governance & Cyber Law',
            'roles': {
                'AI Ethics, Policy & Algorithmic Auditor': ['AI Safety & Algorithmic Bias Auditing', 'Data Privacy Regulation (GDPR/DPDP Act)', 'Technology Contract Negotiation', 'AI Ethics & High-Assurance Computing'],
            }
        },
        'media-creative': {
            'field_name': 'Digital Media & Game Engines',
            'roles': {
                'Real-Time 3D & Virtual Production Architect': ['Unreal Engine 5 Real-Time Rendering', 'Unity Engine Game Development', 'Procedural 3D Modeling (Blender/Houdini)', 'C++ Systems Programming'],
            }
        },
        'supply-chain-logistics': {
            'field_name': 'Autonomous Logistics & Supply Chain',
            'roles': {
                'Autonomous Fleet & Supply Chain Optimization Lead': ['Supply Chain Network Optimization', 'Autonomous Warehouse Robotics Routing', 'SQL Advanced Query Optimization', 'Python Programming'],
            }
        },
        'marine-ocean': {
            'field_name': 'Ocean Engineering & Blue Economy',
            'roles': {
                'Autonomous Underwater Vehicle (AUV) Systems Engineer': ['Autonomous Underwater Vehicle Navigation', 'Marine Hydrodynamics & Hull Modeling', 'Embedded C & Microcontrollers', 'Robot Operating System (ROS 2)'],
            }
        }
    }

    field_slug = request.GET.get('field', '').strip()
    target_role = request.GET.get('role', '').strip()

    all_roles_by_field = {}
    flat_role_map = {}
    for fslug, fval in FIELD_CAREER_MAP.items():
        all_roles_by_field[fslug] = {
            'field_name': fval['field_name'],
            'roles': list(fval['roles'].keys())
        }
        for rtitle, rskills in fval['roles'].items():
            flat_role_map[rtitle] = {
                'field_slug': fslug,
                'field_name': fval['field_name'],
                'skills': rskills
            }

    if not field_slug or field_slug not in FIELD_CAREER_MAP:
        if target_role and target_role in flat_role_map:
            field_slug = flat_role_map[target_role]['field_slug']
        else:
            field_slug = 'computer-science'

    roles_in_field = FIELD_CAREER_MAP[field_slug]['roles']
    if not target_role or target_role not in flat_role_map:
        target_role = list(roles_in_field.keys())[0]

    current_role_info = flat_role_map.get(target_role)
    required_skill_names = current_role_info['skills']

    required_skills = []
    for sname in required_skill_names:
        sk = Skill.objects.filter(name__iexact=sname).first()
        if not sk:
            sk = Skill.objects.filter(name__icontains=sname.split()[0]).first()
        if sk:
            required_skills.append(sk)

    if not required_skills:
        required_skills = list(Skill.objects.filter(field__slug=field_slug)[:5])

    matched_skills = [s for s in required_skills if s.id in user_skill_ids or s.name in user_skill_names]
    missing_skills = [s for s in required_skills if s not in matched_skills]

    total_req = max(len(required_skills), 1)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    match_percentage = int((matched_count / total_req) * 100)
    gap_percentage = max(100 - match_percentage, 0)

    missing_fields = [s.field for s in missing_skills if s.field]
    if missing_fields:
        recommended_courses = Course.objects.filter(field__in=missing_fields).distinct()[:4]
    else:
        recommended_courses = Course.objects.filter(field__slug=field_slug)[:4]

    if missing_fields:
        recommended_certifications = Certification.objects.filter(field__in=missing_fields).distinct()[:3]
    else:
        recommended_certifications = Certification.objects.filter(field__slug=field_slug)[:3]

    relevant_opportunities = Opportunity.objects.filter(field__slug=field_slug)[:3]

    context = {
        'is_faculty_view': False,
        'field_slug': field_slug,
        'target_role': target_role,
        'current_role_info': current_role_info,
        'FIELD_CAREER_MAP': FIELD_CAREER_MAP,
        'all_roles_by_field': all_roles_by_field,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'user_skills': user_skills_qs,
        'required_skills': required_skills,
        'matched_count': matched_count,
        'missing_count': missing_count,
        'total_required': total_req,
        'match_percentage': match_percentage,
        'gap_percentage': gap_percentage,
        'recommended_courses': recommended_courses,
        'recommended_certifications': recommended_certifications,
        'relevant_opportunities': relevant_opportunities,
    }
    return render(request, 'pages/skill_gap.html', context)
