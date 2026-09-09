from django.test import TestCase
from apps.skills.models import Skill, UserSkill, DigitalSkillPassport
from apps.accounts.models import User

class SkillModelTest(TestCase):
    def test_skill_passport_creation(self):
        user = User.objects.create_user(
            email='passportstudent@aicportal.edu',
            password='Password123!',
            first_name='Passport',
            last_name='User'
        )
        passport = DigitalSkillPassport.objects.create(
            user=user,
            passport_number='AIC-TEST-9900'
        )
        self.assertTrue(passport.is_verified)
        self.assertIn('/passport/verify/', passport.get_public_url())

    def test_smart_skill_gap_analysis(self):
        from django.urls import reverse
        from apps.taxonomy.models import Field, FieldType
        
        field = Field.objects.create(name='Computer Science & AI', slug='computer-science', category=FieldType.TECHNICAL)
        sk_python = Skill.objects.create(name='Python Programming', slug='python-prog', field=field)
        sk_pytorch = Skill.objects.create(name='PyTorch Deep Learning', slug='pytorch-dl', field=field)
        sk_llm = Skill.objects.create(name='Large Language Models (LLMs)', slug='llms', field=field)

        user = User.objects.create_user(
            email='gapstudent@aicportal.edu',
            password='Password123!',
            first_name='Gap',
            last_name='Student'
        )
        # Assign only Python to user
        UserSkill.objects.create(user=user, skill=sk_python)

        self.client.force_login(user)
        response = self.client.get(reverse('skill_gap'), {'field': 'computer-science', 'role': 'AI & Machine Learning Systems Architect'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Target Career Role: AI &amp; Machine Learning Systems Architect')
        self.assertContains(response, 'Present Verified Skills')
        self.assertContains(response, 'Desired Skills Needed')
        self.assertContains(response, 'Python Programming')
        self.assertContains(response, 'PyTorch Deep Learning')
        
        # Verify readiness and gap percentage computations
        self.assertIn('match_percentage', response.context)
        self.assertIn('gap_percentage', response.context)
        self.assertEqual(response.context['matched_count'], 1)
        self.assertGreaterEqual(response.context['missing_count'], 1)
        self.assertEqual(response.context['match_percentage'] + response.context['gap_percentage'], 100)
