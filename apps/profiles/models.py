import os
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ProfileVisibility(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Public'
    REGISTERED_USERS = 'REGISTERED_USERS', 'Registered Users Only'
    CONNECTIONS_ONLY = 'CONNECTIONS_ONLY', 'Connections Only'
    PRIVATE = 'PRIVATE', 'Private'

def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/user_{instance.user.id}/photo.{ext}"

def profile_thumb_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/user_{instance.user.id}/thumb_256.{ext}"

class UserProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    headline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    google_scholar_url = models.URLField(blank=True, null=True)
    
    # Photo Management System
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=profile_thumb_path, blank=True, null=True)
    photo_uploaded_at = models.DateTimeField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    
    visibility = models.CharField(
        max_length=25,
        choices=ProfileVisibility.choices,
        default=ProfileVisibility.REGISTERED_USERS
    )
    completion_percentage = models.IntegerField(default=20)

    # Role-Specific & Global Settings Preferences
    job_search_status = models.CharField(
        max_length=30,
        default='ACTIVELY_LOOKING',
        choices=[
            ('ACTIVELY_LOOKING', 'Actively Looking for Opportunities'),
            ('OPEN', 'Open to Relevant Roles'),
            ('NOT_LOOKING', 'Not Looking Currently')
        ]
    )
    mentorship_available = models.BooleanField(default=True)
    candidate_match_threshold = models.IntegerField(default=70) # For Industry recruiters (min match %)
    email_notifications = models.BooleanField(default=True)
    job_alerts = models.BooleanField(default=True)
    digest_frequency = models.CharField(
        max_length=20,
        default='WEEKLY',
        choices=[
            ('INSTANT', 'Instant Alerts'),
            ('DAILY', 'Daily Digest'),
            ('WEEKLY', 'Weekly Summary'),
            ('OFF', 'Off')
        ]
    )
    preferred_theme = models.CharField(max_length=20, default='LIGHT')

    def get_avatar_initials(self):
        first = self.user.first_name[:1].upper() if self.user.first_name else ''
        last = self.user.last_name[:1].upper() if self.user.last_name else ''
        return f"{first}{last}" or self.user.email[:2].upper()

    def calculate_completion(self):
        score = 20
        if self.profile_photo:
            score += 20
        if self.headline:
            score += 15
        if self.bio:
            score += 15
        if self.location:
            score += 10
        if self.linkedin_url or self.github_url or self.website:
            score += 20
        self.completion_percentage = min(score, 100)
        return self.completion_percentage

    def save(self, *args, **kwargs):
        self.calculate_completion()
        super().save(*args, **kwargs)
        
        # Process profile photo & generate cropped 256x256 thumbnail
        if self.profile_photo and not self.thumbnail:
            try:
                img = Image.open(self.profile_photo.path)
                img = ImageOps.fit(img, (256, 256), Image.Resampling.LANCZOS)
                
                thumb_io = BytesIO()
                fmt = 'PNG' if self.profile_photo.name.lower().endswith('.png') else 'JPEG'
                img.save(thumb_io, format=fmt, quality=90)
                
                thumb_filename = f"thumb_{os.path.basename(self.profile_photo.name)}"
                self.thumbnail.save(thumb_filename, ContentFile(thumb_io.getvalue()), save=False)
                super().save(update_fields=['thumbnail'])
            except Exception:
                pass

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"
