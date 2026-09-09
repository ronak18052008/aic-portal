import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, PrimaryRole
from apps.opportunities.models import Opportunity, OpportunityType
from apps.skills.models import Skill, UserSkill
from apps.applications.models import Application, ApplicationStatus

def seed_talent_and_applications():
    print("Seeding recruiter talent matching and applications...")

    # 1. Ensure TechCorp Global Solutions has proper jobs with required skills
    recruiter = User.objects.filter(primary_role=PrimaryRole.INDUSTRY, email='recruiter@aic.com').first()
    if not recruiter:
        print("Recruiter recruiter@aic.com not found!")
        return

    python_skill = Skill.objects.filter(slug='python').first()
    django_skill = Skill.objects.filter(slug='django').first()
    sql_skill = Skill.objects.filter(slug='sql').first()
    pytorch_skill = Skill.objects.filter(slug='pytorch').first()
    pandas_skill = Skill.objects.filter(slug='pandas').first()
    react_skill = Skill.objects.filter(slug='react').first()
    docker_skill = Skill.objects.filter(slug='docker').first()

    # Get or create TechCorp Opportunities
    techcorp_jobs = [
        {
            'title': 'AI Backend Systems Engineer',
            'slug': 'ai-backend-systems-eng-techcorp',
            'type': OpportunityType.JOB,
            'skills': [s for s in [python_skill, django_skill, docker_skill, sql_skill] if s],
            'stipend': 2400000.00,
            'period': 'Per Annum',
            'desc': 'Build scalable microservices and asynchronous backend architectures supporting generative AI and real-time inference pipelines.'
        },
        {
            'title': 'Data Science & Machine Learning Associate',
            'slug': 'ds-ml-associate-techcorp',
            'type': OpportunityType.JOB,
            'skills': [s for s in [python_skill, pytorch_skill, pandas_skill, sql_skill] if s],
            'stipend': 1800000.00,
            'period': 'Per Annum',
            'desc': 'Develop predictive machine learning models, statistical analyses, and high-performance data processing pipelines.'
        },
        {
            'title': 'Full Stack Cloud Development Intern',
            'slug': 'fullstack-cloud-intern-techcorp',
            'type': OpportunityType.INTERNSHIP,
            'skills': [s for s in [python_skill, react_skill, django_skill] if s],
            'stipend': 45000.00,
            'period': 'Per Month',
            'desc': 'Hands-on cloud engineering internship working on modern full-stack web applications and cloud deployment architectures.'
        }
    ]

    cs_field = Skill.objects.filter(slug='python').first().field if python_skill else None

    created_opps = []
    for jdef in techcorp_jobs:
        opp, created = Opportunity.objects.update_or_create(
            slug=jdef['slug'],
            defaults={
                'title': jdef['title'],
                'organization_name': recruiter.organization_name or 'TechCorp Global Solutions',
                'opportunity_type': jdef['type'],
                'field': cs_field,
                'stipend_salary': jdef['stipend'],
                'salary_period': jdef['period'],
                'description': jdef['desc'],
                'country': 'India',
                'state': 'Karnataka',
                'city': 'Bengaluru',
                'is_verified': True,
                'verification_source': 'TechCorp Enterprise Recruitment Board',
                'official_apply_url': 'https://techcorp.com/careers'
            }
        )
        if jdef['skills']:
            opp.required_skills.set(jdef['skills'])
        created_opps.append(opp)
        print(f"Set up opportunity: {opp.title} with {opp.required_skills.count()} required skills.")

    # 2. Seed realistic applications from real students
    students = list(User.objects.filter(primary_role=PrimaryRole.STUDENT))
    print(f"Found {len(students)} students.")

    cover_notes = [
        "I have strong hands-on experience building Django microservices and deploying models in containerized environments.",
        "Excited to apply for this position. My skill passport verifies my proficiency in Python, Machine Learning, and SQL.",
        "I recently completed the AIC Full-Stack certification and capstone project. Looking forward to contributing to your backend engineering team.",
        "My coursework and research focus on distributed data processing with Pandas and NumPy. I would love to bring my expertise to TechCorp.",
        "Passionate about modern cloud engineering and full stack development. I have built multiple production-grade React & Django apps.",
        "I scored in the top 95th percentile on the AIC Adaptive Assessment for Python Programming and Deep Learning."
    ]

    statuses = [
        ApplicationStatus.APPLIED,
        ApplicationStatus.SCREENING,
        ApplicationStatus.ASSESSMENT,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.OFFER
    ]

    app_count = 0
    for idx, student in enumerate(students):
        target_opp = created_opps[idx % len(created_opps)]
        status = statuses[idx % len(statuses)]
        note = cover_notes[idx % len(cover_notes)]

        app, created = Application.objects.update_or_create(
            applicant=student,
            opportunity=target_opp,
            defaults={
                'status': status,
                'cover_note': note,
                'is_external_redirect': False,
                'official_redirect_url': target_opp.official_apply_url
            }
        )
        app_count += 1
        print(f"Application: {student.get_full_name()} -> {target_opp.title} [{status}]")

    print(f"Successfully seeded {app_count} applications across TechCorp opportunities!")

if __name__ == '__main__':
    seed_talent_and_applications()
