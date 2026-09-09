import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.taxonomy.models import Field, Subfield
from apps.education.models import Course, Programme, Certification
from apps.opportunities.models import Opportunity
from apps.skills.models import Skill
from apps.institutions.models import Institution

print("=== FIELDS ===")
for f in Field.objects.all():
    print(f"- {f.name} (slug: {f.slug}, category: {f.category}, subfields: {f.subfields.count()})")

print("\n=== DEMO DATA AUDIT ===")
print("Fields containing 'Demo' or '#':", Field.objects.filter(name__icontains='demo').count())
print("Courses containing '#' or 'Demo':", Course.objects.filter(title__contains='#').count())
print("Programmes containing '#' or 'Demo':", Programme.objects.filter(title__contains='#').count())
print("Opportunities containing '#' or 'Demo':", Opportunity.objects.filter(title__contains='#').count())
print("Skills containing '#' or 'Demo':", Skill.objects.filter(name__contains='#').count())
print("Institutions containing '#' or 'Demo':", Institution.objects.filter(name__contains='#').count())
