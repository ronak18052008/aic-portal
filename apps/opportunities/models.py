from django.db import models
from apps.core.models import BaseModel
from apps.taxonomy.models import Field, Subfield
from apps.skills.models import Skill

class OpportunityType(models.TextChoices):
    JOB = 'JOB', 'Job'
    INTERNSHIP = 'INTERNSHIP', 'Internship'
    APPRENTICESHIP = 'APPRENTICESHIP', 'Apprenticeship'
    FELLOWSHIP = 'FELLOWSHIP', 'Fellowship'
    SCHOLARSHIP = 'SCHOLARSHIP', 'Scholarship'
    PROJECT = 'PROJECT', 'Industry Project'

class OpportunityMode(models.TextChoices):
    REMOTE = 'REMOTE', 'Remote'
    HYBRID = 'HYBRID', 'Hybrid'
    ON_SITE = 'ON_SITE', 'On-Site'

class Opportunity(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    organization_name = models.CharField(max_length=255)
    opportunity_type = models.CharField(max_length=30, choices=OpportunityType.choices, default=OpportunityType.JOB)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='opportunities')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True)
    
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    mode = models.CharField(max_length=20, choices=OpportunityMode.choices, default=OpportunityMode.HYBRID)
    
    description = models.TextField()
    responsibilities = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    
    required_skills = models.ManyToManyField(Skill, related_name='opportunities', blank=True)
    stipend_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='INR')
    salary_period = models.CharField(max_length=20, default='Monthly') # Per Month, Annual
    
    deadline = models.DateField(blank=True, null=True)
    official_apply_url = models.URLField()
    is_verified = models.BooleanField(default=True)
    verification_source = models.CharField(max_length=150, default='Official Portal')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} @ {self.organization_name} ({self.get_opportunity_type_display()})"
