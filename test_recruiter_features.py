import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.accounts.models import User, PrimaryRole
from apps.applications.models import Application, ApplicationStatus
from apps.core.views import dashboard_view, manage_applications_view, update_application_status_api

def test_recruiter_features():
    recruiter = User.objects.filter(primary_role=PrimaryRole.INDUSTRY, email='recruiter@aic.com').first()
    rf = RequestFactory()

    # 1. Test Recruiter Dashboard
    req = rf.get('/dashboard/')
    req.user = recruiter
    resp = dashboard_view(req)
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert '% Match' in content
    print("SUCCESS: Recruiter Dashboard test passed with talent match %.")

    # 2. Test ATS View
    req2 = rf.get('/applications/manage/')
    req2.user = recruiter
    resp2 = manage_applications_view(req2)
    assert resp2.status_code == 200
    content2 = resp2.content.decode('utf-8')
    assert 'Applicant Tracking System' in content2
    print("SUCCESS: ATS Manage View test passed.")

    # 3. Test Status Transition API
    app = Application.objects.first()
    req3 = rf.post(
        '/api/applications/update-status/',
        data=json.dumps({'application_id': str(app.id), 'status': 'INTERVIEW'}),
        content_type='application/json'
    )
    req3.user = recruiter
    resp3 = update_application_status_api(req3)
    assert resp3.status_code == 200
    data = json.loads(resp3.content.decode('utf-8'))
    assert data['success'] is True
    app.refresh_from_db()
    assert app.status == 'INTERVIEW'
    print(f"SUCCESS: Application stage transition API test passed: new status = {app.status}")

if __name__ == '__main__':
    test_recruiter_features()
