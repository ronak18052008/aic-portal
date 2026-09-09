from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class SavedSearch(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, default='COURSES') # COURSES, PROGRAMMES, JOBS, UNIVERSITIES
    query_params = models.JSONField(default=dict)
    enable_alert = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} saved search: {self.title}"
