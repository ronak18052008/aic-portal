from django.contrib import admin
from .models import (
    SkillNode, StudentSkillProfile, SkillEvidence,
    SkillDemandSnapshot, SkillSupplySnapshot,
    IndustryChallenge, ChallengeParticipant, ChallengeTeam,
    ChallengeTeamMember, ChallengeTask, ChallengeSubmission,
    SubmissionEvaluation
)

@admin.register(SkillNode)
class SkillNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'category', 'industry_demand_score']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(StudentSkillProfile)
class StudentSkillProfileAdmin(admin.ModelAdmin):
    list_display = ['student', 'skill_node', 'score', 'confidence_score', 'is_verified']
    list_filter = ['proficiency', 'is_verified']

@admin.register(SkillEvidence)
class SkillEvidenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'skill_node', 'evidence_type', 'score_percentage', 'is_approved']
    list_filter = ['evidence_type', 'is_approved']

@admin.register(IndustryChallenge)
class IndustryChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization_name', 'difficulty', 'status', 'deadline']
    list_filter = ['status', 'difficulty']
    search_fields = ['title', 'organization_name']

@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['student', 'challenge', 'stage', 'progress_pct']
    list_filter = ['stage']

@admin.register(ChallengeSubmission)
class ChallengeSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'participant', 'challenge', 'is_final', 'submitted_at']

@admin.register(SubmissionEvaluation)
class SubmissionEvaluationAdmin(admin.ModelAdmin):
    list_display = ['submission', 'evaluator', 'total_score', 'evaluated_at']

admin.site.register(SkillDemandSnapshot)
admin.site.register(SkillSupplySnapshot)
admin.site.register(ChallengeTeam)
admin.site.register(ChallengeTeamMember)
admin.site.register(ChallengeTask)
