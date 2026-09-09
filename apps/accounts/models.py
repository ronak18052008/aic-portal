import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class PrimaryRole(models.TextChoices):
    STUDENT = 'STUDENT', 'Student'
    ACADEMICIAN = 'ACADEMICIAN', 'Academician'
    INDUSTRY = 'INDUSTRY', 'Industry'
    INSTITUTION = 'INSTITUTION', 'Institution'
    SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'System Administrator'

class SubRole(models.TextChoices):
    # Student
    STUDENT_GENERAL = 'STUDENT_GENERAL', 'Student'
    
    # Academician
    FACULTY = 'FACULTY', 'Faculty'
    PROFESSOR = 'PROFESSOR', 'Professor'
    RESEARCHER = 'RESEARCHER', 'Researcher'
    FACULTY_MENTOR = 'FACULTY_MENTOR', 'Faculty Mentor'
    ACADEMIC_DEPT_COORD = 'ACADEMIC_DEPT_COORD', 'Department Coordinator'
    ACADEMIC_RESEARCH_COORD = 'ACADEMIC_RESEARCH_COORD', 'Research Coordinator'
    
    # Industry
    COMPANY_ADMIN = 'COMPANY_ADMIN', 'Company Admin'
    HR = 'HR', 'HR Manager'
    RECRUITER = 'RECRUITER', 'Recruiter'
    INDUSTRY_MENTOR = 'INDUSTRY_MENTOR', 'Industry Mentor'
    INDUSTRY_EXPERT = 'INDUSTRY_EXPERT', 'Industry Expert'
    TRAINING_COORD = 'TRAINING_COORD', 'Training Coordinator'
    INDUSTRY_RESEARCH_COORD = 'INDUSTRY_RESEARCH_COORD', 'Industry Research Coordinator'
    
    # Institution
    INSTITUTION_ADMIN = 'INSTITUTION_ADMIN', 'Institution Admin'
    PRINCIPAL = 'PRINCIPAL', 'Principal'
    DIRECTOR = 'DIRECTOR', 'Director'
    HOD = 'HOD', 'Head of Department (HOD)'
    TPO = 'TPO', 'Training & Placement Officer (TPO)'
    PLACEMENT_OFFICER = 'PLACEMENT_OFFICER', 'Placement Officer'
    INST_DEPT_COORD = 'INST_DEPT_COORD', 'Department Coordinator'
    SKILL_COORD = 'SKILL_COORD', 'Skill Coordinator'
    INST_RESEARCH_COORD = 'INST_RESEARCH_COORD', 'Research Coordinator'

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('primary_role', PrimaryRole.SYSTEM_ADMIN)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    primary_role = models.CharField(
        max_length=30,
        choices=PrimaryRole.choices,
        default=PrimaryRole.STUDENT
    )
    sub_role = models.CharField(
        max_length=40,
        choices=SubRole.choices,
        default=SubRole.STUDENT_GENERAL
    )
    
    # Permission Scope
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_primary_role_display()})"
