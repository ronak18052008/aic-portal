from django.test import TestCase
from django.urls import reverse
from apps.taxonomy.models import Field, FieldType
from apps.education.models import Course, ModeType

class SearchTest(TestCase):
    def test_global_search_view(self):
        field = Field.objects.create(name='AI Test Field', slug='ai-test-field', category=FieldType.TECHNICAL)
        Course.objects.create(
            title='Python Deep Learning Course',
            slug='python-dl-course',
            provider='NPTEL',
            field=field,
            description='Deep learning with Python',
            mode=ModeType.ONLINE,
            official_url='https://swayam.gov.in'
        )
        response = self.client.get(reverse('global_search'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Deep Learning Course')

    def test_institutions_directory_filter(self):
        from apps.institutions.models import Institution, InstitutionType
        inst = Institution.objects.create(
            name='IIT Delhi',
            slug='iit-delhi',
            institution_type=InstitutionType.TECHNICAL_INSTITUTE,
            city='New Delhi',
            country='India'
        )
        response = self.client.get(reverse('institutions_list'), {'institution': 'iit-delhi'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IIT Delhi')
        self.assertEqual(response.context['institution_filter'], 'iit-delhi')

    def test_search_institution_filter(self):
        from apps.institutions.models import Institution, InstitutionType
        from apps.education.models import Programme, Certification, ProgrammeType, CertificationLevel
        from apps.opportunities.models import Opportunity, OpportunityType

        field = Field.objects.create(name='Computing Field', slug='comp-field', category=FieldType.TECHNICAL)
        inst1 = Institution.objects.create(
            name='IIT Bombay',
            slug='iit-bombay',
            institution_type=InstitutionType.TECHNICAL_INSTITUTE,
            city='Mumbai',
            country='India'
        )
        inst2 = Institution.objects.create(
            name='MIT USA',
            slug='mit-usa',
            institution_type=InstitutionType.UNIVERSITY,
            city='Cambridge',
            country='United States'
        )
        
        from apps.taxonomy.models import EducationLevel
        edu_level = EducationLevel.objects.create(name='Postgraduate', code='PG', order=2)

        # Associated with IIT Bombay
        prog1 = Programme.objects.create(
            institution=inst1,
            title='M.Tech AI IIT Bombay',
            slug='mtech-ai-iitb',
            field=field,
            level=edu_level,
            programme_type=ProgrammeType.DEGREE,
            mode=ModeType.OFFLINE,
            duration_months=24,
            credits=64,
            official_url='https://iitb.ac.in'
        )
        # Associated with MIT
        prog2 = Programme.objects.create(
            institution=inst2,
            title='MS CS MIT',
            slug='ms-cs-mit',
            field=field,
            level=edu_level,
            programme_type=ProgrammeType.DEGREE,
            mode=ModeType.OFFLINE,
            duration_months=24,
            credits=64,
            official_url='https://mit.edu'
        )
        # Unrelated course
        Course.objects.create(
            title='Harvard CS50',
            slug='harvard-cs50',
            provider='edX / Harvard',
            field=field,
            mode=ModeType.ONLINE,
            official_url='https://edx.org'
        )
        # Course matching IIT Bombay
        Course.objects.create(
            title='IIT Bombay NPTEL ML',
            slug='iitb-nptel-ml',
            provider='NPTEL IIT Bombay',
            field=field,
            mode=ModeType.ONLINE,
            official_url='https://swayam.gov.in'
        )

        # Filter by institution slug
        response = self.client.get(reverse('global_search'), {'institution': 'iit-bombay'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IIT Bombay')
        self.assertContains(response, 'M.Tech AI IIT Bombay')
        self.assertContains(response, 'IIT Bombay NPTEL ML')
        self.assertNotContains(response, 'MS CS MIT')
        self.assertNotContains(response, 'Harvard CS50')
        self.assertEqual(response.context['facet_counts']['programmes'], 1)
        self.assertEqual(response.context['facet_counts']['courses'], 1)
        self.assertEqual(response.context['facet_counts']['institutions'], 1)
        self.assertEqual(response.context['facet_counts']['jobs'], 0)
        self.assertEqual(response.context['facet_counts']['certifications'], 0)

