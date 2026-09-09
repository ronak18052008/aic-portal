from django.db import models
from apps.core.models import BaseModel

class FieldType(models.TextChoices):
    TECHNICAL = 'TECHNICAL', 'Technical'
    NATURAL_SCIENCES = 'NATURAL_SCIENCES', 'Natural Sciences'
    MEDICAL_HEALTH = 'MEDICAL_HEALTH', 'Medical & Health'
    BUSINESS_MANAGEMENT = 'BUSINESS_MANAGEMENT', 'Business & Management'
    ARTS_HUMANITIES = 'ARTS_HUMANITIES', 'Arts & Humanities'
    LAW = 'LAW', 'Law'
    EDUCATION = 'EDUCATION', 'Education'
    SOCIAL_SCIENCES = 'SOCIAL_SCIENCES', 'Social Sciences'
    DESIGN_CREATIVE = 'DESIGN_CREATIVE', 'Design & Creative'
    AGRICULTURE_FOOD = 'AGRICULTURE_FOOD', 'Agriculture & Food'
    ENVIRONMENT_SUSTAINABILITY = 'ENVIRONMENT_SUSTAINABILITY', 'Environment & Sustainability'
    MEDIA_COMMUNICATION = 'MEDIA_COMMUNICATION', 'Media & Communication'
    SPORTS = 'SPORTS', 'Sports'
    VOCATIONAL_SKILLED = 'VOCATIONAL_SKILLED', 'Vocational & Skilled Trades'
    INTERDISCIPLINARY = 'INTERDISCIPLINARY', 'Interdisciplinary'

class Field(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.CharField(max_length=40, choices=FieldType.choices, default=FieldType.TECHNICAL)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='academic-cap')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Subfield(BaseModel):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='subfields')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('field', 'slug')
        ordering = ['name']

    def __str__(self):
        return f"{self.field.name} -> {self.name}"

class Specialization(BaseModel):
    subfield = models.ForeignKey(Subfield, on_delete=models.CASCADE, related_name='specializations')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)

    class Meta:
        unique_together = ('subfield', 'slug')

    def __str__(self):
        return f"{self.subfield.name} -> {self.name}"

class EducationLevel(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    isced_level = models.CharField(max_length=20, blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
