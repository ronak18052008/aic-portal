from django.db import models
from apps.core.models import BaseModel
from apps.taxonomy.models import Field, Subfield, EducationLevel
from apps.institutions.models import Institution, Department

class ModeType(models.TextChoices):
    ONLINE = 'ONLINE', 'Online'
    OFFLINE = 'OFFLINE', 'On-Campus / Offline'
    HYBRID = 'HYBRID', 'Hybrid'

class ProgrammeType(models.TextChoices):
    DEGREE = 'DEGREE', 'Degree'
    DIPLOMA = 'DIPLOMA', 'Diploma'
    CERTIFICATE = 'CERTIFICATE', 'Certificate'
    BOOTCAMP = 'BOOTCAMP', 'Bootcamp'
    FELLOWSHIP = 'FELLOWSHIP', 'Fellowship'
    RESEARCH_PROGRAMME = 'RESEARCH_PROGRAMME', 'Research Programme'
    EXCHANGE_PROGRAMME = 'EXCHANGE_PROGRAMME', 'Exchange Programme'
    EXECUTIVE_EDUCATION = 'EXECUTIVE_EDUCATION', 'Executive Education'

class Programme(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    programme_type = models.CharField(max_length=40, choices=ProgrammeType.choices, default=ProgrammeType.DEGREE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='programmes')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='programmes')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey(EducationLevel, on_delete=models.CASCADE)
    
    description = models.TextField()
    learning_outcomes = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    duration_months = models.IntegerField(default=24)
    credits = models.IntegerField(default=120)
    mode = models.CharField(max_length=20, choices=ModeType.choices, default=ModeType.OFFLINE)
    
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='INR')
    has_scholarship = models.BooleanField(default=False)
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    official_url = models.URLField()
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.institution.name}"

class Course(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    provider = models.CharField(max_length=150, help_text='University, Coursera, NPTEL, edX, AIC Platform')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='courses')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True)
    instructor = models.CharField(max_length=150, blank=True, null=True)
    
    description = models.TextField()
    level_name = models.CharField(max_length=50, default='Intermediate')
    duration_hours = models.IntegerField(default=40)
    mode = models.CharField(max_length=20, choices=ModeType.choices, default=ModeType.ONLINE)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='INR')
    provides_certificate = models.BooleanField(default=True)
    
    rating = models.FloatField(default=4.5)
    enrolled_count = models.IntegerField(default=0)
    official_url = models.URLField()
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-rating', 'title']

    def __str__(self):
        return f"{self.title} ({self.provider})"

class CourseModule(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Mod {self.order}: {self.title}"


class CertificationLevel(models.TextChoices):
    FOUNDATIONAL = 'FOUNDATIONAL', 'Foundational / Entry'
    ASSOCIATE = 'ASSOCIATE', 'Associate'
    PROFESSIONAL = 'PROFESSIONAL', 'Professional'
    SPECIALTY = 'SPECIALTY', 'Specialty / Expert'


class Certification(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    issuing_organization = models.CharField(max_length=255, help_text='e.g. AWS, Google Cloud, Microsoft, Cisco, NPTEL')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='certifications')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True)
    credential_code = models.CharField(max_length=100, blank=True, null=True, help_text='e.g. SAA-C03, AZ-900, CKA, CISSP')
    level = models.CharField(max_length=30, choices=CertificationLevel.choices, default=CertificationLevel.ASSOCIATE)
    
    description = models.TextField()
    exam_format = models.CharField(max_length=150, default='Online Proctored / Authorized Test Center')
    duration_minutes = models.IntegerField(default=120)
    validity_years = models.IntegerField(default=3)
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='INR')
    
    skills_covered = models.ManyToManyField('skills.Skill', related_name='certifications', blank=True)
    official_verify_url = models.URLField(help_text='Official exam registration or certificate verification portal')
    is_verified = models.BooleanField(default=True)
    verification_source = models.CharField(max_length=150, default='Official Issuing Body')

    class Meta:
        ordering = ['issuing_organization', 'title']

    def __str__(self):
        return f"{self.title} ({self.issuing_organization})"


# ──────────────────────────────────────────────────────────────────────────────
# Events, Workshops & Seminars
# ──────────────────────────────────────────────────────────────────────────────

class EventType(models.TextChoices):
    CONFERENCE   = 'CONFERENCE',   'Conference'
    WORKSHOP     = 'WORKSHOP',     'Workshop'
    SEMINAR      = 'SEMINAR',      'Seminar'
    HACKATHON    = 'HACKATHON',    'Hackathon'
    WEBINAR      = 'WEBINAR',      'Webinar'
    FDP          = 'FDP',          'Faculty Development Programme (FDP)'
    SYMPOSIUM    = 'SYMPOSIUM',    'Symposium'
    BOOTCAMP     = 'BOOTCAMP',     'Bootcamp'
    PANEL        = 'PANEL',        'Panel Discussion'
    EXPO         = 'EXPO',         'Tech Expo / Industry Fair'

class EventMode(models.TextChoices):
    ONLINE   = 'ONLINE',   'Online / Virtual'
    OFFLINE  = 'OFFLINE',  'On-Campus / In-Person'
    HYBRID   = 'HYBRID',   'Hybrid'

class Event(BaseModel):
    title            = models.CharField(max_length=255)
    slug             = models.SlugField(max_length=255, unique=True)
    event_type       = models.CharField(max_length=30, choices=EventType.choices, default=EventType.SEMINAR)
    mode             = models.CharField(max_length=20, choices=EventMode.choices, default=EventMode.HYBRID)

    # Organizer details
    organizer_name   = models.CharField(max_length=255, help_text='e.g. IIT Bombay CSE Dept, NASSCOM, Google India')
    department       = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    institution      = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    field            = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True)

    # Schedule
    start_date       = models.DateField()
    end_date         = models.DateField(blank=True, null=True)
    start_time       = models.TimeField(blank=True, null=True)
    registration_deadline = models.DateField(blank=True, null=True)

    # Venue & access
    venue            = models.CharField(max_length=255, blank=True, null=True, help_text='e.g. Seminar Hall A, VMCC Building, IIT Bombay')
    city             = models.CharField(max_length=100, default='Bengaluru')
    state            = models.CharField(max_length=100, default='Karnataka')
    country          = models.CharField(max_length=100, default='India')
    online_platform  = models.CharField(max_length=150, blank=True, null=True, help_text='e.g. Google Meet, Zoom, MS Teams')
    meeting_link     = models.URLField(blank=True, null=True)

    # Content details
    description      = models.TextField()
    speakers         = models.TextField(blank=True, null=True, help_text='Comma-separated speaker names and titles')
    topics_covered   = models.TextField(blank=True, null=True, help_text='Comma-separated key topics')
    target_audience  = models.CharField(max_length=255, default='Students, Faculty, Researchers')
    prerequisites    = models.TextField(blank=True, null=True)
    outcome          = models.TextField(blank=True, null=True, help_text='What attendees will gain')

    # Registration & capacity
    max_registrations = models.IntegerField(default=200)
    is_free          = models.BooleanField(default=True)
    registration_fee  = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    provides_certificate = models.BooleanField(default=True)
    official_url     = models.URLField(blank=True, null=True)

    # Status
    is_verified      = models.BooleanField(default=True)
    is_featured      = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_date', 'title']

    def __str__(self):
        return f"{self.get_event_type_display()}: {self.title} ({self.organizer_name})"


class EventRegistration(BaseModel):
    """Tracks student registrations for Events, Workshops, and Seminars."""
    event      = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student    = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    is_attended   = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'student')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.event.title}"
