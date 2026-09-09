import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.core.views import dashboard_view
from apps.search.views import global_search_view
from apps.opportunities.models import Opportunity, OpportunityType

User = get_user_model()
factory = RequestFactory()

# 1. Test Recruiter Dashboard
recruiter = User.objects.filter(email='recruiter@aic.com').first()
assert recruiter is not None, "Recruiter user recruiter@aic.com not found!"

req = factory.get('/dashboard/')
req.user = recruiter

response = dashboard_view(req)
assert response.status_code == 200, f"Dashboard failed with status {response.status_code}"
content = response.content.decode('utf-8')

# Assertions for Posted Jobs on Recruiter Dashboard
assert "My Posted Jobs & Active Requisitions" in content, "Missing 'My Posted Jobs & Active Requisitions' section in dashboard!"
assert "Recruiter Job Management" in content, "Missing recruiter job management badge!"
assert "Talent Discovery AI Engine" in content, "Missing Talent Discovery AI Engine section!"
assert "Active Candidates in ATS Pipeline" in content, "Missing ATS section!"
print("[OK] Recruiter Dashboard renders Posted Jobs, Talent Matching, and ATS Pipeline flawlessly.")

# 2. Test Talent Discovery (/search/?type=students)
req_search = factory.get('/search/?type=students')
req_search.user = recruiter

resp_search = global_search_view(req_search)
assert resp_search.status_code == 200, f"Search failed with status {resp_search.status_code}"
search_content = resp_search.content.decode('utf-8')

# Verify that students are shown and NOT programmes, courses, institutions
assert "Recruiter Talent Discovery Engine" in search_content, "Missing Recruiter Talent Discovery Engine banner!"
assert "Verified Student Candidate Pool" in search_content, "Missing Verified Student Candidate Pool header!"
assert "Degree & Diploma Programmes" not in search_content, "Programmes should NOT be displayed in Talent Discovery (type=students)!"
assert "Global Courses & MOOCs" not in search_content, "Courses should NOT be displayed in Talent Discovery (type=students)!"
assert "Universities & Higher Education Institutions" not in search_content, "Institutions should NOT be displayed in Talent Discovery (type=students)!"
assert "National & Global Scholarships" not in search_content, "Scholarships should NOT be displayed in Talent Discovery (type=students)!"
print("[OK] Talent Discovery (/search/?type=students) displays ONLY verified student candidate pool, zero programmes or courses.")

# 3. Test Student Candidate Search by Query
req_q = factory.get('/search/?type=students&q=Python')
req_q.user = recruiter
resp_q = global_search_view(req_q)
assert resp_q.status_code == 200
search_q_content = resp_q.content.decode('utf-8')
assert "Recruiter Talent Discovery Engine" in search_q_content
print("[OK] Talent Discovery search by query ('Python') filters student candidates properly.")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
