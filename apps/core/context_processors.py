from apps.profiles.models import UserProfile
from apps.notifications.models import Notification
from apps.applications.models import Application

def aic_global_context(request):
    context = {
        'aic_logo_url': '/static/images/aic_logo.jpg',
        'unread_notifications_count': 0,
        'active_applications_count': 0,
        'user_profile': None,
        'current_role': 'GUEST',
        'sidebar_categories': [],
    }

    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        context['user_profile'] = profile
        context['unread_notifications_count'] = Notification.objects.filter(recipient=request.user, is_read=False).count()
        context['active_applications_count'] = Application.objects.filter(applicant=request.user).count()
        context['current_role'] = request.user.primary_role
        
        # Build dynamic role-aware hierarchical sidebar
        role = request.user.primary_role
        
        if role == 'STUDENT':
            context['sidebar_categories'] = [
                {
                    'title': 'Overview',
                    'icon': 'home',
                    'items': [
                        {'name': 'Dashboard', 'url': '/dashboard/', 'badge': None},
                        {'name': 'My AIC Passport', 'url': '/passport/', 'badge': 'Verified'},
                        {'name': 'AI Resume Builder', 'url': '/resume/builder/', 'badge': 'AI'},
                        {'name': 'AI Career Roadmap', 'url': '/career/roadmap/', 'badge': 'AI'},
                        {'name': 'AI Chatbot Assistant', 'url': '/chatbot/', 'badge': 'Online'},
                    ]
                },
                {
                    'title': 'Education & Learning',
                    'icon': 'academic-cap',
                    'items': [
                        {'name': 'Universities & Colleges', 'url': '/institutions/', 'badge': None},
                        {'name': 'Degree Programmes', 'url': '/search/?type=programmes', 'badge': None},
                        {'name': 'Global Courses', 'url': '/search/?type=courses', 'badge': None},
                        {'name': 'Certifications', 'url': '/certifications/', 'badge': 'Verified'},
                    ]
                },
                {
                    'title': 'Skills & Assessments',
                    'icon': 'light-bulb',
                    'items': [
                        {'name': 'My Skill Intelligence', 'url': '/skills/', 'badge': None},
                        {'name': 'Skill Genome', 'url': '/skill-genome/', 'badge': 'DNA'},
                        {'name': 'Skill Gap Analysis', 'url': '/skills/gap/', 'badge': 'Smart'},
                        {'name': 'Industry Skill Map', 'url': '/skill-intelligence/', 'badge': 'Live'},
                        {'name': 'Adaptive Assessments', 'url': '/skills/assessments/', 'badge': None},
                    ]
                },
                {
                    'title': 'Opportunities & Career',
                    'icon': 'briefcase',
                    'items': [
                        {'name': 'Job Recruitment', 'url': '/search/?type=jobs', 'badge': None},
                        {'name': 'Internships & Apprenticeships', 'url': '/search/?type=internships', 'badge': None},
                        {'name': 'Industry Challenges', 'url': '/challenges/', 'badge': 'Hot'},
                        {'name': 'My Challenges', 'url': '/challenges/my/', 'badge': None},
                        {'name': 'My Applications', 'url': '/applications/', 'badge': str(context['active_applications_count'])},
                        {'name': 'Scholarships & Fellowships', 'url': '/search/?type=scholarships', 'badge': None},
                    ]
                },
                {
                    'title': 'Research & Settings',
                    'icon': 'cog',
                    'items': [
                        {'name': 'Research Projects', 'url': '/research/', 'badge': None},
                        {'name': 'Find Industry Mentors', 'url': '/mentorship/', 'badge': None},
                        {'name': 'Events & Workshops', 'url': '/events/', 'badge': 'Register'},
                        {'name': 'Settings & Privacy', 'url': '/settings/', 'badge': None},
                    ]
                }
            ]
        elif role == 'ACADEMICIAN':
            context['sidebar_categories'] = [
                {
                    'title': 'Academic Hub',
                    'icon': 'home',
                    'items': [
                        {'name': 'Academician Dashboard', 'url': '/dashboard/', 'badge': None},
                        {'name': 'Universities & Colleges', 'url': '/institutions/', 'badge': 'Global'},
                        {'name': 'AI Academic Advisor', 'url': '/chatbot/', 'badge': 'Online'},
                        {'name': 'Faculty Skills & FDP', 'url': '/skills/', 'badge': None},
                        {'name': 'Student Skill Genome', 'url': '/skill-genome/', 'badge': 'DNA'},
                        {'name': 'Skill Intelligence', 'url': '/skill-intelligence/', 'badge': 'Gap'},
                        {'name': 'Curriculum Gap Analysis', 'url': '/skills/gap/', 'badge': None},
                    ]
                },
                {
                    'title': 'Research & Projects',
                    'icon': 'beaker',
                    'items': [
                        {'name': 'Research Projects & Grants', 'url': '/research/', 'badge': None},
                        {'name': 'Industry Collaborations', 'url': '/search/?type=projects', 'badge': None},
                        {'name': 'Student Mentorship', 'url': '/mentorship/', 'badge': None},
                    ]
                },
                {
                    'title': 'Industry Opportunities & Settings',
                    'icon': 'cog',
                    'items': [
                        {'name': 'Faculty Internships', 'url': '/search/?type=internships', 'badge': None},
                        {'name': 'Consultancy Projects', 'url': '/search/?type=jobs', 'badge': None},
                        {'name': 'Events & Workshops', 'url': '/events/', 'badge': 'Upcoming'},
                        {'name': 'Faculty Settings', 'url': '/settings/', 'badge': None},
                    ]
                }
            ]
        elif role == 'INDUSTRY':
            context['sidebar_categories'] = [
                {
                    'title': 'Talent & Hiring',
                    'icon': 'office-building',
                    'items': [
                        {'name': 'Industry Dashboard', 'url': '/dashboard/', 'badge': None},
                        {'name': 'Universities & Colleges', 'url': '/institutions/', 'badge': 'Global'},
                        {'name': 'AI Recruitment Copilot', 'url': '/chatbot/', 'badge': 'Online'},
                        {'name': 'Talent Discovery Engine', 'url': '/search/?type=students', 'badge': 'AI Match'},
                        {'name': 'Industry Challenges', 'url': '/challenges/', 'badge': 'New'},
                        {'name': 'Post a Challenge', 'url': '/challenges/create/', 'badge': 'Create'},
                        {'name': 'Skill Intelligence', 'url': '/skill-intelligence/', 'badge': 'Data'},
                        {'name': 'Post Job / Internship', 'url': '/opportunities/create/', 'badge': 'New'},
                        {'name': 'Applicant Tracking', 'url': '/applications/manage/', 'badge': None},
                    ]
                },
                {
                    'title': 'Academia Partnerships & Settings',
                    'icon': 'cog',
                    'items': [
                        {'name': 'Project Marketplace', 'url': '/search/?type=projects', 'badge': None},
                        {'name': 'Joint Research Grants', 'url': '/research/', 'badge': None},
                        {'name': 'Industry Mentors', 'url': '/mentorship/', 'badge': None},
                        {'name': 'Events & Workshops', 'url': '/events/', 'badge': 'Network'},
                        {'name': 'Recruiter Settings', 'url': '/settings/', 'badge': None},
                    ]
                }
            ]
        elif role == 'INSTITUTION':
            context['sidebar_categories'] = [
                {
                    'title': 'Institution Management',
                    'icon': 'academic-cap',
                    'items': [
                        {'name': 'Institution Dashboard', 'url': '/dashboard/', 'badge': None},
                        {'name': 'Universities & Colleges', 'url': '/institutions/', 'badge': 'Directory'},
                        {'name': 'AI Campus Intelligence', 'url': '/chatbot/', 'badge': 'Online'},
                        {'name': 'Department Heatmap', 'url': '/institutions/heatmap/', 'badge': 'Analytics'},
                        {'name': 'Curriculum-Industry Gap', 'url': '/skills/gap/', 'badge': None},
                        {'name': 'Placement Intelligence', 'url': '/institutions/placement/', 'badge': 'Predictive'},
                    ]
                },
                {
                    'title': 'Industry Connections & Settings',
                    'icon': 'cog',
                    'items': [
                        {'name': 'Industry Partners', 'url': '/industry/partners/', 'badge': 'MoUs'},
                        {'name': 'Campus Recruitment', 'url': '/recruitment/campus/', 'badge': 'Live'},
                        {'name': 'Events & Workshops', 'url': '/events/', 'badge': 'Upcoming'},
                        {'name': 'Verification Center', 'url': '/admin/verification/', 'badge': 'Audit'},
                        {'name': 'Institution Settings', 'url': '/settings/', 'badge': None},
                    ]
                }
            ]
        else: # System Admin
            context['sidebar_categories'] = [
                {
                    'title': 'System Admin Control',
                    'icon': 'cog',
                    'items': [
                        {'name': 'Admin Dashboard', 'url': '/dashboard/', 'badge': 'Global'},
                        {'name': 'Verification Center', 'url': '/admin/verification/', 'badge': 'Audit'},
                        {'name': 'Skill Genome Monitor', 'url': '/skill-genome/', 'badge': 'DNA'},
                        {'name': 'Skill Intelligence', 'url': '/skill-intelligence/', 'badge': 'Gap'},
                        {'name': 'Industry Challenges', 'url': '/challenges/admin/', 'badge': 'Monitor'},
                        {'name': 'Campus Recruitment', 'url': '/recruitment/campus/', 'badge': 'Live'},
                        {'name': 'Industry Partners', 'url': '/industry/partners/', 'badge': 'MoUs'},
                        {'name': 'Curriculum-Industry Gap', 'url': '/skills/gap/', 'badge': 'Cohort'},
                        {'name': 'Events & Workshops', 'url': '/events/', 'badge': 'Live'},
                        {'name': 'Universities & Colleges', 'url': '/institutions/', 'badge': 'Directory'},
                        {'name': 'AI Admin Copilot', 'url': '/chatbot/', 'badge': 'Online'},
                        {'name': 'Source Health & Provenance', 'url': '/sources/', 'badge': 'Sync'},
                        {'name': 'Taxonomy Configuration', 'url': '/admin/taxonomy/', 'badge': None},
                        {'name': 'System Settings', 'url': '/settings/', 'badge': None},
                        {'name': 'Django Superuser Panel', 'url': '/admin/', 'badge': 'Core'},
                    ]
                }
            ]

    return context
