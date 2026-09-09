from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.taxonomy.models import Field

class ResearchProject(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    organization_name = models.CharField(max_length=255)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='research_projects')
    lead_researcher = models.CharField(max_length=150)
    
    abstract = models.TextField()
    collaborators_needed = models.CharField(max_length=255, blank=True, null=True)
    grant_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='INR')
    
    start_date = models.DateField(blank=True, null=True)
    official_url = models.URLField()
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.organization_name}"

class MentorshipPair(BaseModel):
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_pairings')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentee_pairings')
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='ACTIVE')
    meeting_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Mentor: {self.mentor.get_full_name()} -> Mentee: {self.mentee.get_full_name()}"
