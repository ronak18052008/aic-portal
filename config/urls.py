from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import (
    home_view, login_view, register_view, logout_view,
    dashboard_view, profile_view, passport_view, passport_public_verify_view,
    notifications_view, career_roadmap_view, assessments_view,
    research_view, mentorship_view, create_opportunity_view,
    manage_applications_view, institution_heatmap_view,
    institution_placement_view, taxonomy_admin_view,
    institutions_list_view, certifications_list_view,
    chatbot_view, chatbot_api, settings_view, captcha_refresh_api,
    faculty_add_skill_api, faculty_propose_collab_api, update_application_status_api,
    industry_partners_view, campus_recruitment_view, export_placements_csv_view,
    admin_verification_center_view, admin_verify_action_api,
    events_view, event_register_api
)
from apps.profiles.resume_views import (
    resume_builder_view, resume_download_pdf_view, resume_ai_enhance_api
)
from apps.search.views import global_search_view
from apps.skills.views import skills_overview_view, skill_gap_view, submit_assessment_api
from apps.applications.views import applications_list_view, apply_opportunity_view
from apps.sources.views import sources_provenance_view
from apps.genome.views import (
    skill_genome_view, skill_node_detail_view, add_evidence_api, approve_evidence_api,
    skill_intelligence_view, supply_demand_api,
    challenges_view, challenge_detail_view, participate_challenge_api,
    my_challenges_view, challenge_workspace_view, submit_challenge_api,
    evaluate_challenge_view, save_evaluation_api, update_pipeline_api,
    challenge_pipeline_view, create_challenge_view, challenges_admin_view,
)

urlpatterns = [
    # Admin Custom Authority & Verification (placed before django admin site)
    path('admin/verification/', admin_verification_center_view, name='admin_verification'),
    path('admin/taxonomy/', taxonomy_admin_view, name='taxonomy_admin'),
    path('admin/', admin.site.urls),
    
    # Public & Auth
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('api/captcha/refresh/', captcha_refresh_api, name='captcha_refresh'),
    
    # Core User Views
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('passport/', passport_view, name='passport'),
    path('passport/verify/<uuid:token>/', passport_public_verify_view, name='passport_verify'),
    path('notifications/', notifications_view, name='notifications'),
    path('career/roadmap/', career_roadmap_view, name='career_roadmap'),
    path('settings/', settings_view, name='settings'),

    # AI Resume & CV Studio
    path('resume/builder/', resume_builder_view, name='resume_builder'),
    path('resume/download-pdf/', resume_download_pdf_view, name='resume_download_pdf'),
    path('api/resume/ai-enhance/', resume_ai_enhance_api, name='resume_ai_enhance'),

    # Role-Aware AI Chatbot
    path('chatbot/', chatbot_view, name='chatbot'),
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
    
    # Search & Smart Filters
    path('search/', global_search_view, name='global_search'),
    path('certifications/', certifications_list_view, name='certifications_list'),
    
    # Skills Intelligence & Gap Engine
    path('skills/', skills_overview_view, name='skills_overview'),
    path('skills/gap/', skill_gap_view, name='skill_gap'),
    path('skills/assessments/', assessments_view, name='assessments'),
    path('api/assessments/submit/', submit_assessment_api, name='submit_assessment_api'),
    path('api/faculty/add-skill/', faculty_add_skill_api, name='faculty_add_skill_api'),
    path('api/faculty/propose-collab/', faculty_propose_collab_api, name='faculty_propose_collab_api'),
    
    # Opportunities & Recruitment
    path('opportunities/create/', create_opportunity_view, name='create_opportunity'),
    path('opportunities/<uuid:opportunity_id>/apply/', apply_opportunity_view, name='apply_opportunity'),
    
    # Research & Mentorship
    path('research/', research_view, name='research'),
    path('mentorship/', mentorship_view, name='mentorship'),
    
    # Applications Lifecycle
    path('applications/', applications_list_view, name='applications_list'),
    path('applications/manage/', manage_applications_view, name='manage_applications'),
    path('api/applications/update-status/', update_application_status_api, name='update_application_status_api'),
    
    # Institution Intelligence & Collaborations
    path('institutions/', institutions_list_view, name='institutions_list'),
    path('institutions/heatmap/', institution_heatmap_view, name='institution_heatmap'),
    path('institutions/placement/', institution_placement_view, name='institution_placement'),
    path('industry/partners/', industry_partners_view, name='industry_partners'),
    path('recruitment/campus/', campus_recruitment_view, name='campus_recruitment'),
    path('recruitment/campus/export-csv/', export_placements_csv_view, name='export_placements_csv'),
    
    # Admin System & Verification API
    path('admin-center/verification/', admin_verification_center_view, name='admin_verification_alias'),
    path('api/admin/verify/', admin_verify_action_api, name='admin_verify_action'),

    # Events, Workshops & Seminars Hub
    path('events/', events_view, name='events'),
    path('api/events/register/', event_register_api, name='event_register_api'),

    # Verification & Provenance
    path('sources/', sources_provenance_view, name='sources_provenance'),

    # ── Skill Genome + Skill Provenance ─────────────────────────────────────
    path('skill-genome/', skill_genome_view, name='skill_genome'),
    path('skill-genome/node/<uuid:node_id>/', skill_node_detail_view, name='skill_node_detail'),
    path('api/genome/evidence/add/', add_evidence_api, name='add_evidence_api'),
    path('api/genome/evidence/approve/', approve_evidence_api, name='approve_evidence_api'),

    # ── Industry Skill Intelligence (Supply-Demand) ──────────────────────────
    path('skill-intelligence/', skill_intelligence_view, name='skill_intelligence'),
    path('api/genome/supply-demand/', supply_demand_api, name='supply_demand_api'),

    # ── Industry Challenges → Talent Pipeline ───────────────────────────────
    path('challenges/', challenges_view, name='challenges'),
    path('challenges/create/', create_challenge_view, name='create_challenge'),
    path('challenges/my/', my_challenges_view, name='my_challenges'),
    path('challenges/admin/', challenges_admin_view, name='challenges_admin'),
    path('challenges/<slug:slug>/', challenge_detail_view, name='challenge_detail'),
    path('challenges/<slug:slug>/workspace/', challenge_workspace_view, name='challenge_workspace'),
    path('challenges/<slug:slug>/evaluate/', evaluate_challenge_view, name='evaluate_challenge'),
    path('challenges/<slug:slug>/pipeline/', challenge_pipeline_view, name='challenge_pipeline'),
    path('api/challenges/participate/', participate_challenge_api, name='participate_challenge_api'),
    path('api/challenges/submit/', submit_challenge_api, name='submit_challenge_api'),
    path('api/challenges/evaluate/', save_evaluation_api, name='save_evaluation_api'),
    path('api/challenges/pipeline/update/', update_pipeline_api, name='update_pipeline_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
