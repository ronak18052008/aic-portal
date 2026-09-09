from django.db import models
from apps.core.models import BaseModel
from apps.taxonomy.models import Field

class InstitutionType(models.TextChoices):
    UNIVERSITY = 'UNIVERSITY', 'University'
    COLLEGE = 'COLLEGE', 'College'
    INSTITUTE = 'INSTITUTE', 'Institute'
    TECHNICAL_INSTITUTE = 'TECHNICAL_INSTITUTE', 'Technical Institute'
    MEDICAL_INSTITUTE = 'MEDICAL_INSTITUTE', 'Medical Institute'
    BUSINESS_SCHOOL = 'BUSINESS_SCHOOL', 'Business School'
    LAW_SCHOOL = 'LAW_SCHOOL', 'Law School'
    RESEARCH_CENTRE = 'RESEARCH_CENTRE', 'Research Centre'
    POLYTECHNIC = 'POLYTECHNIC', 'Polytechnic'
    OPEN_UNIVERSITY = 'OPEN_UNIVERSITY', 'Open University'
    VOCATIONAL_INSTITUTE = 'VOCATIONAL_INSTITUTE', 'Vocational Institute'

class Institution(BaseModel):
    name = models.CharField(max_length=255)
    official_name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    institution_type = models.CharField(
        max_length=40,
        choices=InstitutionType.choices,
        default=InstitutionType.UNIVERSITY
    )
    logo = models.ImageField(upload_to='institutions/logos/', blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Accreditation & Directory Registration
    aishe_code = models.CharField(max_length=50, blank=True, null=True)
    ugc_recognized = models.BooleanField(default=True)
    naac_grade = models.CharField(max_length=10, blank=True, null=True)
    nirf_rank = models.IntegerField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=True)
    official_apply_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.country})"

class Department(BaseModel):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=150)
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True)
    head_of_department = models.CharField(max_length=150, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    class Meta:
        unique_together = ('institution', 'name')

    def __str__(self):
        return f"{self.institution.name} - {self.name}"
