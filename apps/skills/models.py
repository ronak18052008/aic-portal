import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.taxonomy.models import Field

class SkillProficiency(models.TextChoices):
    BEGINNER = 'BEGINNER', 'Beginner'
    ELEMENTARY = 'ELEMENTARY', 'Elementary'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
    ADVANCED = 'ADVANCED', 'Advanced'
    EXPERT = 'EXPERT', 'Expert'

class SkillEvidence(models.TextChoices):
    SELF_DECLARED = 'SELF_DECLARED', 'Self Declared'
    ASSESSMENT = 'ASSESSMENT', 'Assessment Verified'
    COURSE = 'COURSE', 'Course Completed'
    CERTIFICATE = 'CERTIFICATE', 'Certificate Verified'
    PROJECT = 'PROJECT', 'Project Verified'
    INTERNSHIP = 'INTERNSHIP', 'Internship Experience'
    MENTOR_VERIFIED = 'MENTOR_VERIFIED', 'Mentor Endorsed'
    INDUSTRY_VERIFIED = 'INDUSTRY_VERIFIED', 'Industry Verified'

class Skill(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True, related_name='skills')
    category = models.CharField(max_length=100, default='Core Technical')
    description = models.TextField(blank=True, null=True)
    industry_demand_score = models.IntegerField(default=85) # 0-100 score

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"

class UserSkill(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=SkillProficiency.choices, default=SkillProficiency.INTERMEDIATE)
    evidence_type = models.CharField(max_length=30, choices=SkillEvidence.choices, default=SkillEvidence.SELF_DECLARED)
    score_percentage = models.IntegerField(default=75)
    verified_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.skill.name} ({self.proficiency})"

class AssessmentType(models.TextChoices):
    TECHNICAL = 'TECHNICAL', 'Technical Skill Assessment'
    APTITUDE = 'APTITUDE', 'Aptitude & Reasoning'
    CODING = 'CODING', 'Coding & Data Structures'
    DOMAIN = 'DOMAIN', 'Domain Specialization'
    EMPLOYABILITY = 'EMPLOYABILITY', 'Employability Readiness'

class Assessment(BaseModel):
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=30, choices=AssessmentType.choices, default=AssessmentType.TECHNICAL)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='assessments')
    duration_minutes = models.IntegerField(default=30)
    total_questions = models.IntegerField(default=10)
    pass_mark = models.IntegerField(default=70) # percentage

    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"

class Question(BaseModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    explanation = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, default='MEDIUM')

    def __str__(self):
        return f"Q: {self.question_text[:50]}"

class DigitalSkillPassport(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passport')
    passport_number = models.CharField(max_length=50, unique=True)
    qr_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=True)
    issued_date = models.DateField(auto_now_add=True)

    def get_public_url(self):
        return f"/passport/verify/{self.qr_verification_token}/"

    def __str__(self):
        return f"Passport #{self.passport_number} ({self.user.get_full_name()})"
