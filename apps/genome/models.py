import uuid
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.skills.models import Skill
from apps.taxonomy.models import Field

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — SKILL GENOME + SKILL PROVENANCE
# ══════════════════════════════════════════════════════════════════════════════

class SkillCategory(models.TextChoices):
    PROGRAMMING     = 'PROGRAMMING',     'Programming & Development'
    DATA            = 'DATA',            'Data & Analytics'
    AI_ML           = 'AI_ML',           'Artificial Intelligence & ML'
    CLOUD           = 'CLOUD',           'Cloud & DevOps'
    CYBERSECURITY   = 'CYBERSECURITY',   'Cybersecurity'
    DESIGN          = 'DESIGN',          'Design & UX'
    BUSINESS        = 'BUSINESS',        'Business & Management'
    CORE_ENG        = 'CORE_ENG',        'Core Engineering'
    BIOMEDICAL      = 'BIOMEDICAL',      'Biomedical & Life Sciences'
    LEGAL           = 'LEGAL',           'Law & Governance'
    AGRICULTURE     = 'AGRICULTURE',     'Agriculture & Environment'
    GENERAL         = 'GENERAL',         'General & Soft Skills'


class ProficiencyLevel(models.TextChoices):
    BEGINNER     = 'BEGINNER',     'Beginner'
    ELEMENTARY   = 'ELEMENTARY',   'Elementary'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
    ADVANCED     = 'ADVANCED',     'Advanced'
    EXPERT       = 'EXPERT',       'Expert'


class SkillNode(BaseModel):
    """
    Hierarchical sub-skill node.
    parent=None  → top-level skill (e.g. Python)
    parent=<id>  → sub-skill (e.g. NumPy, OOP, Pandas)
    """
    name        = models.CharField(max_length=150)
    slug        = models.SlugField(max_length=150, unique=True)
    parent      = models.ForeignKey('self', on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='children')
    skill       = models.ForeignKey(Skill, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='nodes')
    category    = models.CharField(max_length=30, choices=SkillCategory.choices,
                                   default=SkillCategory.PROGRAMMING)
    field       = models.ForeignKey(Field, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='skill_nodes')
    description = models.TextField(blank=True, null=True)
    icon        = models.CharField(max_length=60, default='fa-solid fa-code')
    order       = models.IntegerField(default=0)
    industry_demand_score = models.IntegerField(default=50,
        help_text='0-100 relative demand from industry job postings')

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    @property
    def is_root(self):
        return self.parent is None

    def get_all_descendants(self):
        nodes = list(self.children.all())
        for child in self.children.all():
            nodes.extend(child.get_all_descendants())
        return nodes


class EvidenceType(models.TextChoices):
    SELF_DECLARED      = 'SELF_DECLARED',      'Self Declared'
    COURSE             = 'COURSE',             'Course Completed'
    ASSESSMENT         = 'ASSESSMENT',         'Assessment Passed'
    PROJECT            = 'PROJECT',            'Project Submitted'
    CERTIFICATION      = 'CERTIFICATION',      'Certification Earned'
    INTERNSHIP         = 'INTERNSHIP',         'Internship Completed'
    INDUSTRY_CHALLENGE = 'INDUSTRY_CHALLENGE', 'Industry Challenge'
    FACULTY_VERIFIED   = 'FACULTY_VERIFIED',   'Faculty Verified'
    COMPANY_VERIFIED   = 'COMPANY_VERIFIED',   'Company Verified'
    EVENT_WORKSHOP     = 'EVENT_WORKSHOP',     'Workshop / Event Attended'
    LAB_PRACTICAL      = 'LAB_PRACTICAL',      'Lab / Practical Work'

# Confidence weight per evidence type (max raw ≈ 200 for full confidence)
EVIDENCE_WEIGHTS = {
    'SELF_DECLARED':      5,
    'COURSE':            15,
    'ASSESSMENT':        25,
    'PROJECT':           20,
    'CERTIFICATION':     25,
    'INTERNSHIP':        30,
    'INDUSTRY_CHALLENGE':35,
    'FACULTY_VERIFIED':  20,
    'COMPANY_VERIFIED':  40,
    'EVENT_WORKSHOP':    10,
    'LAB_PRACTICAL':     15,
}


class SkillEvidence(BaseModel):
    """One piece of verified evidence for a student-skill pair."""
    student        = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.CASCADE,
                                       related_name='skill_evidences')
    skill_node     = models.ForeignKey(SkillNode, on_delete=models.CASCADE,
                                       related_name='evidences')
    evidence_type  = models.CharField(max_length=30, choices=EvidenceType.choices,
                                      default=EvidenceType.SELF_DECLARED)
    source_title   = models.CharField(max_length=255,
        help_text='e.g. "Python Fundamentals — NPTEL", "AI Challenge #1024"')
    source_url     = models.URLField(blank=True, null=True)
    score_percentage = models.IntegerField(default=0,
        help_text='Score if applicable (0 if not)')
    verified_by    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       related_name='verifications_given')
    verified_at    = models.DateTimeField(null=True, blank=True)
    is_approved    = models.BooleanField(default=False,
        help_text='True only if a faculty/company/admin explicitly approved this')
    notes          = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.get_full_name()} | {self.skill_node.name} | {self.evidence_type}'

    @property
    def confidence_weight(self):
        return EVIDENCE_WEIGHTS.get(self.evidence_type, 5)


class StudentSkillProfile(BaseModel):
    """Aggregated skill profile entry per student per SkillNode."""
    student          = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.CASCADE,
                                         related_name='genome_profiles')
    skill_node       = models.ForeignKey(SkillNode, on_delete=models.CASCADE,
                                         related_name='student_profiles')
    proficiency      = models.CharField(max_length=20,
                                        choices=ProficiencyLevel.choices,
                                        default=ProficiencyLevel.BEGINNER)
    score            = models.IntegerField(default=0,
        help_text='0-100 numerical proficiency score')
    confidence_score = models.IntegerField(default=0,
        help_text='0-100 computed confidence based on evidence weights')
    evidence_count   = models.IntegerField(default=0)
    is_verified      = models.BooleanField(default=False,
        help_text='True if at least one approved non-self-declared evidence exists')
    target_proficiency = models.CharField(max_length=20,
                                          choices=ProficiencyLevel.choices,
                                          null=True, blank=True)
    last_updated     = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('student', 'skill_node')
        ordering = ['skill_node__category', 'skill_node__order']

    def __str__(self):
        return f'{self.student.get_full_name()} — {self.skill_node.name} ({self.score}%)'

    def recalculate(self):
        """Recompute score, confidence, proficiency from evidence."""
        evidences = SkillEvidence.objects.filter(
            student=self.student, skill_node=self.skill_node
        )
        self.evidence_count = evidences.count()
        raw_weight = sum(EVIDENCE_WEIGHTS.get(e.evidence_type, 5) for e in evidences)
        self.confidence_score = min(100, int(raw_weight / 1.5))
        approved = evidences.filter(is_approved=True).exclude(
            evidence_type='SELF_DECLARED'
        )
        self.is_verified = approved.exists()
        scores = [e.score_percentage for e in evidences if e.score_percentage > 0]
        self.score = int(sum(scores) / len(scores)) if scores else 0
        if self.score >= 85:
            self.proficiency = ProficiencyLevel.EXPERT
        elif self.score >= 70:
            self.proficiency = ProficiencyLevel.ADVANCED
        elif self.score >= 50:
            self.proficiency = ProficiencyLevel.INTERMEDIATE
        elif self.score >= 30:
            self.proficiency = ProficiencyLevel.ELEMENTARY
        else:
            self.proficiency = ProficiencyLevel.BEGINNER
        self.save()


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — INDUSTRY SKILL SUPPLY–DEMAND GRAPH
# ══════════════════════════════════════════════════════════════════════════════

class DemandSource(models.TextChoices):
    PORTAL_JOBS         = 'PORTAL_JOBS',         'Portal Job Postings'
    PORTAL_INTERNSHIPS  = 'PORTAL_INTERNSHIPS',  'Portal Internship Postings'
    PORTAL_CHALLENGES   = 'PORTAL_CHALLENGES',   'Industry Challenges'
    EMPLOYER_SURVEY     = 'EMPLOYER_SURVEY',     'Employer Survey'
    IMPORTED            = 'IMPORTED',            'Imported External Data'


class SkillDemandSnapshot(BaseModel):
    """Industry demand snapshot for a skill at a point in time."""
    skill_node    = models.ForeignKey(SkillNode, on_delete=models.CASCADE,
                                      related_name='demand_snapshots')
    demand_score  = models.IntegerField(default=0,
        help_text='Number of open requirements weighted by importance')
    source        = models.CharField(max_length=30, choices=DemandSource.choices,
                                     default=DemandSource.PORTAL_JOBS)
    snapshot_date = models.DateField(auto_now_add=True)
    notes         = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-snapshot_date']

    def __str__(self):
        return f'{self.skill_node.name} demand={self.demand_score} ({self.snapshot_date})'


class SkillSupplySnapshot(BaseModel):
    """Student supply snapshot for a skill at a point in time."""
    skill_node              = models.ForeignKey(SkillNode, on_delete=models.CASCADE,
                                                related_name='supply_snapshots')
    total_students          = models.IntegerField(default=0)
    verified_count          = models.IntegerField(default=0)
    intermediate_plus_count = models.IntegerField(default=0)
    snapshot_date           = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-snapshot_date']

    def __str__(self):
        return f'{self.skill_node.name} supply={self.total_students} ({self.snapshot_date})'


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3 — INDUSTRY CHALLENGE → TALENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

class ChallengeDifficulty(models.TextChoices):
    BEGINNER     = 'BEGINNER',     'Beginner (No prior experience needed)'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate (1–2 years exposure)'
    ADVANCED     = 'ADVANCED',     'Advanced (3+ years / competitive)'
    EXPERT       = 'EXPERT',       'Expert (Research / Production grade)'


class ChallengeStatus(models.TextChoices):
    DRAFT      = 'DRAFT',      'Draft'
    OPEN       = 'OPEN',       'Open for Participation'
    CLOSED     = 'CLOSED',     'Submissions Closed'
    EVALUATING = 'EVALUATING', 'Under Evaluation'
    COMPLETED  = 'COMPLETED',  'Completed'


class ParticipantStage(models.TextChoices):
    REGISTERED  = 'REGISTERED',  'Registered'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    SUBMITTED   = 'SUBMITTED',   'Submitted'
    EVALUATED   = 'EVALUATED',   'Evaluated'
    SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
    INTERVIEW   = 'INTERVIEW',   'Interview Scheduled'
    INTERNSHIP  = 'INTERNSHIP',  'Internship Offered'
    JOB_OFFER   = 'JOB_OFFER',   'Job Offer Extended'
    REJECTED    = 'REJECTED',    'Not Selected'


class IndustryChallenge(BaseModel):
    """A real-world problem posted by a company for students to solve."""
    title              = models.CharField(max_length=255)
    slug               = models.SlugField(max_length=255, unique=True)
    company_user       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                           on_delete=models.CASCADE,
                                           related_name='posted_challenges')
    organization_name  = models.CharField(max_length=255)
    field              = models.ForeignKey(Field, on_delete=models.SET_NULL,
                                           null=True, blank=True,
                                           related_name='challenges')
    problem_statement  = models.TextField()
    description        = models.TextField()
    difficulty         = models.CharField(max_length=20,
                                          choices=ChallengeDifficulty.choices,
                                          default=ChallengeDifficulty.INTERMEDIATE)
    duration_weeks     = models.IntegerField(default=4)
    team_min           = models.IntegerField(default=1)
    team_max           = models.IntegerField(default=4)
    deadline           = models.DateTimeField()
    required_skills    = models.ManyToManyField(SkillNode,
                                                related_name='required_by_challenges',
                                                blank=True)
    preferred_skills   = models.ManyToManyField(SkillNode,
                                                 related_name='preferred_by_challenges',
                                                 blank=True)
    evaluation_criteria= models.TextField(blank=True, null=True,
        help_text='JSON string: [{"name": "Technical", "weight": 40}, ...]')
    rewards            = models.TextField(blank=True, null=True)
    opportunity_after  = models.TextField(blank=True, null=True,
        help_text='What students can get after completing this challenge')
    banner_url         = models.URLField(blank=True, null=True)
    status             = models.CharField(max_length=20,
                                          choices=ChallengeStatus.choices,
                                          default=ChallengeStatus.OPEN)
    is_team_challenge  = models.BooleanField(default=False)
    is_verified        = models.BooleanField(default=True)
    max_participants   = models.IntegerField(default=500)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.organization_name}'

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def submission_count(self):
        return self.submissions.count()

    @property
    def is_open(self):
        from django.utils import timezone
        return self.status == ChallengeStatus.OPEN and self.deadline > timezone.now()


class ChallengeParticipant(BaseModel):
    """A student enrolled in a challenge."""
    challenge     = models.ForeignKey(IndustryChallenge, on_delete=models.CASCADE,
                                      related_name='participants')
    student       = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      on_delete=models.CASCADE,
                                      related_name='challenge_participations')
    stage         = models.CharField(max_length=20, choices=ParticipantStage.choices,
                                     default=ParticipantStage.REGISTERED)
    progress_pct  = models.IntegerField(default=0, help_text='0-100 self-reported progress')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('challenge', 'student')
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.student.get_full_name()} → {self.challenge.title} [{self.stage}]'


class ChallengeTeam(BaseModel):
    """Optional team for a challenge."""
    challenge   = models.ForeignKey(IndustryChallenge, on_delete=models.CASCADE,
                                    related_name='teams')
    name        = models.CharField(max_length=150)
    leader      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    related_name='led_teams')
    invite_code = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f'Team: {self.name} ({self.challenge.title})'


class ChallengeTeamMember(BaseModel):
    team    = models.ForeignKey(ChallengeTeam, on_delete=models.CASCADE,
                                related_name='members')
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='team_memberships')

    class Meta:
        unique_together = ('team', 'student')

    def __str__(self):
        return f'{self.student.get_full_name()} in {self.team.name}'


class TaskStatus(models.TextChoices):
    TODO        = 'TODO',        'To Do'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    DONE        = 'DONE',        'Done'


class ChallengeTask(BaseModel):
    """Task in a student/team's challenge workspace."""
    challenge   = models.ForeignKey(IndustryChallenge, on_delete=models.CASCADE,
                                    related_name='tasks')
    participant = models.ForeignKey(ChallengeParticipant, on_delete=models.CASCADE,
                                    related_name='tasks')
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status      = models.CharField(max_length=20, choices=TaskStatus.choices,
                                   default=TaskStatus.TODO)
    due_date    = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['status', 'created_at']

    def __str__(self):
        return f'{self.title} [{self.status}]'


class ChallengeSubmission(BaseModel):
    """Project submission by a student or team."""
    challenge         = models.ForeignKey(IndustryChallenge, on_delete=models.CASCADE,
                                          related_name='submissions')
    participant       = models.ForeignKey(ChallengeParticipant, on_delete=models.CASCADE,
                                          related_name='submissions')
    team              = models.ForeignKey(ChallengeTeam, on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='submissions')
    title             = models.CharField(max_length=255)
    description       = models.TextField()
    github_url        = models.URLField(blank=True, null=True)
    demo_url          = models.URLField(blank=True, null=True)
    documentation_url = models.URLField(blank=True, null=True)
    presentation_url  = models.URLField(blank=True, null=True)
    is_final          = models.BooleanField(default=False,
        help_text='True = final submission, no more edits allowed')
    submitted_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Submission: {self.title} by {self.participant.student.get_full_name()}'


class SubmissionEvaluation(BaseModel):
    """Company evaluator scores a submission."""
    submission           = models.OneToOneField(ChallengeSubmission,
                                                on_delete=models.CASCADE,
                                                related_name='evaluation')
    evaluator            = models.ForeignKey(settings.AUTH_USER_MODEL,
                                             on_delete=models.SET_NULL,
                                             null=True,
                                             related_name='evaluations_given')
    technical_score      = models.IntegerField(default=0, help_text='0-100')
    problem_score        = models.IntegerField(default=0, help_text='0-100')
    innovation_score     = models.IntegerField(default=0, help_text='0-100')
    implementation_score = models.IntegerField(default=0, help_text='0-100')
    documentation_score  = models.IntegerField(default=0, help_text='0-100')
    presentation_score   = models.IntegerField(default=0, help_text='0-100')
    feedback             = models.TextField(blank=True, null=True)
    skills_verified      = models.ManyToManyField(SkillNode,
                                                   related_name='verified_by_evaluations',
                                                   blank=True)
    evaluated_at         = models.DateTimeField(auto_now_add=True)

    @property
    def total_score(self):
        """Weighted: Technical 35%, Problem 20%, Innovation 20%, Impl 10%, Doc 8%, Pres 7%"""
        return round(
            self.technical_score * 0.35 +
            self.problem_score   * 0.20 +
            self.innovation_score* 0.20 +
            self.implementation_score * 0.10 +
            self.documentation_score  * 0.08 +
            self.presentation_score   * 0.07
        )

    def __str__(self):
        return f'Eval: {self.submission} → {self.total_score}/100'
