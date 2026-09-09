from django.test import TestCase
from apps.accounts.models import User, PrimaryRole, SubRole

class UserModelTest(TestCase):
    def test_create_user_with_role(self):
        user = User.objects.create_user(
            email='teststudent@aicportal.edu',
            password='Password123!',
            first_name='Test',
            last_name='Student',
            primary_role=PrimaryRole.STUDENT,
            sub_role=SubRole.STUDENT_GENERAL
        )
        self.assertEqual(user.email, 'teststudent@aicportal.edu')
        self.assertEqual(user.primary_role, PrimaryRole.STUDENT)
        self.assertEqual(user.get_full_name(), 'Test Student')


class NewFeaturesIntegrationTest(TestCase):
    def setUp(self):
        import uuid
        from apps.profiles.models import UserProfile
        from apps.skills.models import DigitalSkillPassport

        self.user = User.objects.create_user(
            email='aryan@aicportal.edu',
            password='Password123!',
            first_name='Aryan',
            last_name='Sharma',
            primary_role=PrimaryRole.STUDENT,
            sub_role=SubRole.STUDENT_GENERAL
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            location='Bengaluru, Karnataka, India',
            headline='AI & Machine Learning Scholar'
        )
        self.passport = DigitalSkillPassport.objects.create(
            user=self.user,
            passport_number='AIC-IND-2026-0001',
            qr_verification_token=uuid.uuid4(),
            is_verified=True
        )

    def test_qr_code_utility(self):
        from apps.skills.qr_utils import generate_qr_code_data_uri
        data_uri = generate_qr_code_data_uri("https://example.com/test")
        self.assertTrue(data_uri.startswith("data:image/png;base64,"))

    def test_passport_view_renders_qr_code(self):
        self.client.force_login(self.user)
        response = self.client.get('/passport/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('qr_code_data_uri', response.context)
        self.assertTrue(response.context['qr_code_data_uri'].startswith("data:image/png;base64,"))

    def test_public_passport_verification_view(self):
        url = f'/passport/verify/{self.passport.qr_verification_token}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Officially Verified Credential')
        self.assertContains(response, 'Aryan Sharma')

    def test_resume_builder_view(self):
        self.client.force_login(self.user)
        response = self.client.get('/resume/builder/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Resume & CV Builder')

    def test_resume_ai_enhance_api(self):
        import json
        self.client.force_login(self.user)
        payload = {
            'action': 'enhance_summary',
            'target_role': 'AI Backend Engineer',
            'skills': ['Python', 'Django']
        }
        response = self.client.post('/api/resume/ai-enhance/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('summaries', data)

    def test_ai_chatbot_api(self):
        import json
        self.client.force_login(self.user)
        payload = {'message': 'How do I apply for scholarships?'}
        response = self.client.post('/api/chatbot/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('reply', data)
        self.assertGreater(len(data['reply']), 10)

    def test_settings_view_and_update(self):
        self.client.force_login(self.user)
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Settings & Configuration')

        post_data = {
            'action': 'account_settings',
            'first_name': 'Aryan',
            'last_name': 'Sharma',
            'headline': 'Updated Lead AI Researcher',
            'location': 'Bengaluru, Karnataka'
        }
        post_response = self.client.post('/settings/', post_data)
        self.assertEqual(post_response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.headline, 'Updated Lead AI Researcher')


