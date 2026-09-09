from django.db import models
from apps.core.models import BaseModel

class SourceType(models.TextChoices):
    GOVERNMENT = 'GOVERNMENT', 'Government Statutory Body (e.g. AISHE, UGC, AICTE)'
    REGULATORY = 'REGULATORY', 'Regulatory Authority'
    UNIVERSITY = 'UNIVERSITY', 'University Official Portal'
    COLLEGE = 'COLLEGE', 'College Official Portal'
    COMPANY = 'COMPANY', 'Official Enterprise Portal'
    VERIFIED_PROVIDER = 'VERIFIED_PROVIDER', 'Verified Course / Certification Provider'

class VerificationStatus(models.TextChoices):
    VERIFIED = 'VERIFIED', 'Verified Record'
    PENDING = 'PENDING', 'Pending Verification'
    CONFLICT = 'CONFLICT', 'Source Conflict Detected'
    BROKEN = 'BROKEN', 'Broken / Unreachable Source'

class Source(BaseModel):
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=40, choices=SourceType.choices, default=SourceType.UNIVERSITY)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class VerificationRecord(BaseModel):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='records')
    entity_type = models.CharField(max_length=100) # Institution, Course, Programme, Opportunity
    entity_id = models.CharField(max_length=100)
    external_id = models.CharField(max_length=150, blank=True, null=True)
    original_url = models.URLField()
    status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    verified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.entity_type} #{self.entity_id} verified by {self.source.name}"

class SourceConflict(BaseModel):
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    source_a_name = models.CharField(max_length=150)
    source_a_value = models.TextField()
    source_b_name = models.CharField(max_length=150)
    source_b_value = models.TextField()
    resolved_value = models.TextField(blank=True, null=True)
    resolution_method = models.CharField(max_length=100, default='Authority Score')

    def __str__(self):
        return f"Conflict in {self.entity_type}.{self.field_name}"
