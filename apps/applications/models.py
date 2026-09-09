from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.opportunities.models import Opportunity

class ApplicationStatus(models.TextChoices):
    APPLIED = 'APPLIED', 'Applied'
    SCREENING = 'SCREENING', 'Under Screening'
    ASSESSMENT = 'ASSESSMENT', 'Assessment Phase'
    SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
    INTERVIEW = 'INTERVIEW', 'Interview Scheduled'
    SELECTED = 'SELECTED', 'Selected'
    OFFER = 'OFFER', 'Offer Extended'
    JOINED = 'JOINED', 'Joined / Accepted'

class Application(BaseModel):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED
    )
    cover_note = models.TextField(blank=True, null=True)
    is_external_redirect = models.BooleanField(default=False)
    official_redirect_url = models.URLField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'opportunity')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} -> {self.opportunity.title} ({self.get_status_display()})"
