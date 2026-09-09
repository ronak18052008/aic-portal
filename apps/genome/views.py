import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Avg, Count, Q, Sum

from apps.genome.models import (
    SkillNode, StudentSkillProfile, SkillEvidence, EvidenceType,
    SkillDemandSnapshot, SkillSupplySnapshot,
    IndustryChallenge, ChallengeParticipant, ChallengeTeam,
    ChallengeTeamMember, ChallengeTask, ChallengeSubmission,
    SubmissionEvaluation, ParticipantStage, EVIDENCE_WEIGHTS,
    SkillCategory
)
from apps.notifications.models import Notification
from apps.accounts.models import User
from apps.skills.models import UserSkill


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _send_notification(recipient, title, message, link=None, ntype='GENOME'):
    Notification.objects.create(
        recipient=recipient, title=title, message=message,
        notification_type=ntype, link=link or ''
    )


def _get_or_create_profile(student, skill_node):
    profile, _ = StudentSkillProfile.objects.get_or_create(
        student=student, skill_node=skill_node
    )
    return profile


def _compute_skill_match(student, challenge):
    """Return (match_pct, matched_nodes, missing_nodes) for a student vs challenge."""
    required = list(challenge.required_skills.all())
    if not required:
        return 100, [], []
    matched, missing = [], []
    for node in required:
        try:
            profile = StudentSkillProfile.objects.get(student=student, skill_node=node)
            if profile.score >= 40:
                matched.append(node)
            else:
                missing.append(node)
        except StudentSkillProfile.DoesNotExist:
            missing.append(node)
    pct = round(len(matched) / len(required) * 100)
    return pct, matched, missing


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — SKILL GENOME
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def skill_genome_view(request):
    """Main Skill Genome page — student sees own genome, others can browse."""
    user = request.user
    role = user.primary_role

    # Which student to show
    student_id = request.GET.get('student_id')
    if student_id and role in ('ACADEMICIAN', 'SYSTEM_ADMIN', 'INSTITUTION'):
        student = get_object_or_404(User, id=student_id, primary_role='STUDENT')
    elif role == 'STUDENT':
        student = user
    else:
        # Non-student viewing own role — show aggregate view
        student = None

    categories_data = []
    overall_score = 0
    total_nodes = 0
    verified_count = 0
    recently_improved = []

    if student:
        # Build genome by category
        root_nodes = SkillNode.objects.filter(parent=None).order_by('category', 'order')
        category_map = {}
        for node in root_nodes:
            cat = node.get_category_display()
            if cat not in category_map:
                category_map[cat] = {'category': cat, 'category_key': node.category, 'skills': []}

            profile = StudentSkillProfile.objects.filter(
                student=student, skill_node=node
            ).first()

            sub_skills = []
            for child in node.children.all():
                child_profile = StudentSkillProfile.objects.filter(
                    student=student, skill_node=child
                ).first()
                sub_skills.append({
                    'node': child,
                    'profile': child_profile,
                    'score': child_profile.score if child_profile else 0,
                    'confidence': child_profile.confidence_score if child_profile else 0,
                    'verified': child_profile.is_verified if child_profile else False,
                })

            category_map[cat]['skills'].append({
                'node': node,
                'profile': profile,
                'score': profile.score if profile else 0,
                'confidence': profile.confidence_score if profile else 0,
                'verified': profile.is_verified if profile else False,
                'evidence_count': profile.evidence_count if profile else 0,
                'sub_skills': sub_skills,
            })

        categories_data = list(category_map.values())

        # Overall score
        all_profiles = StudentSkillProfile.objects.filter(student=student)
        total_nodes = all_profiles.count()
        verified_count = all_profiles.filter(is_verified=True).count()
        if total_nodes:
            overall_score = round(all_profiles.aggregate(avg=Avg('score'))['avg'] or 0)

        recently_improved = all_profiles.filter(
            score__gte=50
        ).order_by('-updated_at')[:5]

    # Students list for faculty/admin
    students_list = None
    if role in ('ACADEMICIAN', 'SYSTEM_ADMIN', 'INSTITUTION'):
        students_list = User.objects.filter(
            primary_role='STUDENT'
        ).order_by('first_name')[:50]

    return render(request, 'pages/skill_genome.html', {
        'student': student,
        'categories_data': categories_data,
        'overall_score': overall_score,
        'total_nodes': total_nodes,
        'verified_count': verified_count,
        'recently_improved': recently_improved,
        'students_list': students_list,
        'role': role,
        'evidence_types': EvidenceType.choices,
        'all_skill_nodes': SkillNode.objects.filter(parent=None).order_by('name'),
    })


@login_required
def skill_node_detail_view(request, node_id):
    """AJAX-friendly node detail — returns JSON for modal."""
    node = get_object_or_404(SkillNode, id=node_id)
    user = request.user

    student_id = request.GET.get('student_id')
    if student_id and user.primary_role in ('ACADEMICIAN', 'SYSTEM_ADMIN', 'INSTITUTION'):
        student = get_object_or_404(User, id=student_id, primary_role='STUDENT')
    elif user.primary_role == 'STUDENT':
        student = user
    else:
        return JsonResponse({'error': 'No student context'}, status=400)

    profile = StudentSkillProfile.objects.filter(student=student, skill_node=node).first()
    evidences = SkillEvidence.objects.filter(student=student, skill_node=node)

    evidence_list = []
    for e in evidences:
        evidence_list.append({
            'type': e.get_evidence_type_display(),
            'type_key': e.evidence_type,
            'source': e.source_title,
            'score': e.score_percentage,
            'approved': e.is_approved,
            'weight': EVIDENCE_WEIGHTS.get(e.evidence_type, 5),
            'date': e.created_at.strftime('%d %b %Y'),
        })

    sub_profiles = []
    for child in node.children.all():
        cp = StudentSkillProfile.objects.filter(student=student, skill_node=child).first()
        sub_profiles.append({
            'name': child.name,
            'score': cp.score if cp else 0,
            'confidence': cp.confidence_score if cp else 0,
            'verified': cp.is_verified if cp else False,
        })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'node_name': node.name,
            'category': node.get_category_display(),
            'description': node.description or '',
            'score': profile.score if profile else 0,
            'confidence': profile.confidence_score if profile else 0,
            'proficiency': profile.get_proficiency_display() if profile else 'Beginner',
            'verified': profile.is_verified if profile else False,
            'evidence_count': profile.evidence_count if profile else 0,
            'evidence': evidence_list,
            'sub_skills': sub_profiles,
        })

    return render(request, 'pages/skill_node_detail.html', {
        'node': node,
        'student': student,
        'profile': profile,
        'evidences': evidences,
        'sub_skills': sub_profiles,
        'role': user.primary_role,
    })


@login_required
@require_POST
def add_evidence_api(request):
    """Faculty / company / admin adds evidence for a student's skill."""
    role = request.user.primary_role
    if role not in ('ACADEMICIAN', 'INDUSTRY', 'SYSTEM_ADMIN', 'INSTITUTION'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    data = json.loads(request.body)
    student_id = data.get('student_id')
    node_id = data.get('node_id')
    evidence_type = data.get('evidence_type', 'FACULTY_VERIFIED')
    source_title = data.get('source_title', '')
    score = int(data.get('score', 0))
    is_approved = data.get('is_approved', True)

    student = get_object_or_404(User, id=student_id, primary_role='STUDENT')
    node = get_object_or_404(SkillNode, id=node_id)

    ev = SkillEvidence.objects.create(
        student=student, skill_node=node,
        evidence_type=evidence_type,
        source_title=source_title,
        score_percentage=score,
        verified_by=request.user,
        verified_at=timezone.now(),
        is_approved=is_approved,
    )
    profile = _get_or_create_profile(student, node)
    profile.recalculate()

    _send_notification(
        student,
        f'New skill evidence added: {node.name}',
        f'{request.user.get_full_name()} added evidence "{source_title}" to your {node.name} skill.',
        link='/skill-genome/'
    )
    return JsonResponse({'success': True, 'confidence': profile.confidence_score})


@login_required
@require_POST
def approve_evidence_api(request):
    """Approve or reject a skill evidence record."""
    role = request.user.primary_role
    if role not in ('ACADEMICIAN', 'INDUSTRY', 'SYSTEM_ADMIN'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    data = json.loads(request.body)
    evidence_id = data.get('evidence_id')
    approved = data.get('approved', True)

    ev = get_object_or_404(SkillEvidence, id=evidence_id)
    ev.is_approved = approved
    ev.verified_by = request.user
    ev.verified_at = timezone.now()
    ev.save()

    profile = _get_or_create_profile(ev.student, ev.skill_node)
    profile.recalculate()

    return JsonResponse({'success': True, 'verified': profile.is_verified})


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — SKILL SUPPLY-DEMAND INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def skill_intelligence_view(request):
    """Industry Skill Intelligence dashboard — supply vs demand charts."""
    role = request.user.primary_role

    # Build supply-demand data from real portal data
    from apps.opportunities.models import Opportunity
    from apps.skills.models import Skill

    nodes = SkillNode.objects.filter(parent=None).order_by('-industry_demand_score')

    supply_demand = []
    for node in nodes:
        # Demand: count opportunities requiring skills linked to this node
        demand_raw = 0
        if node.skill:
            demand_raw = Opportunity.objects.filter(
                required_skills=node.skill, is_verified=True
            ).count() * 15
        # Add challenge demand
        demand_raw += IndustryChallenge.objects.filter(
            required_skills=node, status='OPEN'
        ).count() * 10
        # Factor in the hand-set demand score
        demand_raw += node.industry_demand_score

        # Supply: students with verified/intermediate+ profiles for this node
        supply_total = StudentSkillProfile.objects.filter(skill_node=node).count()
        supply_verified = StudentSkillProfile.objects.filter(
            skill_node=node, is_verified=True
        ).count()
        supply_intermediate_plus = StudentSkillProfile.objects.filter(
            skill_node=node,
            proficiency__in=['INTERMEDIATE', 'ADVANCED', 'EXPERT']
        ).count()

        gap = demand_raw - supply_intermediate_plus
        ratio = round(demand_raw / max(supply_intermediate_plus, 1), 2)

        # Quadrant classification
        mid_demand = 100
        mid_supply = 50
        if demand_raw >= mid_demand and supply_intermediate_plus < mid_supply:
            quadrant = 'CRITICAL_GAP'
            quadrant_label = 'Critical Gap'
        elif demand_raw >= mid_demand and supply_intermediate_plus >= mid_supply:
            quadrant = 'COMPETITIVE'
            quadrant_label = 'Competitive'
        elif demand_raw < mid_demand and supply_intermediate_plus >= mid_supply:
            quadrant = 'OVERSUPPLIED'
            quadrant_label = 'Oversupplied'
        else:
            quadrant = 'EMERGING'
            quadrant_label = 'Emerging'

        supply_demand.append({
            'node': node,
            'demand': demand_raw,
            'supply_total': supply_total,
            'supply_verified': supply_verified,
            'supply_intermediate_plus': supply_intermediate_plus,
            'gap': gap,
            'ratio': ratio,
            'quadrant': quadrant,
            'quadrant_label': quadrant_label,
        })

    # Sort by gap descending for top gaps
    top_gaps = sorted(supply_demand, key=lambda x: -x['gap'])[:10]
    most_demanded = sorted(supply_demand, key=lambda x: -x['demand'])[:5]
    oversupplied = [s for s in supply_demand if s['quadrant'] == 'OVERSUPPLIED'][:5]

    # Student personal view
    personal_gap = None
    if role == 'STUDENT':
        personal_gap = []
        for item in supply_demand[:15]:
            profile = StudentSkillProfile.objects.filter(
                student=request.user, skill_node=item['node']
            ).first()
            personal_gap.append({
                'node': item['node'],
                'demand': item['demand'],
                'my_score': profile.score if profile else 0,
                'my_proficiency': profile.get_proficiency_display() if profile else 'Unstarted',
                'gap': max(0, 60 - (profile.score if profile else 0)),
                'is_gap': (profile.score if profile else 0) < 60,
            })

    # Industry aggregated view
    industry_view = None
    if role == 'INDUSTRY':
        industry_view = []
        for item in supply_demand:
            industry_view.append({
                'node': item['node'],
                'supply_total': item['supply_total'],
                'supply_intermediate_plus': item['supply_intermediate_plus'],
                'supply_verified': item['supply_verified'],
            })

    # Chart.js data
    chart_labels = json.dumps([s['node'].name for s in supply_demand[:20]])
    chart_demand = json.dumps([s['demand'] for s in supply_demand[:20]])
    chart_supply = json.dumps([s['supply_intermediate_plus'] for s in supply_demand[:20]])
    chart_gap = json.dumps([max(0, s['gap']) for s in supply_demand[:20]])

    bubble_data = json.dumps([{
        'x': item['supply_intermediate_plus'],
        'y': item['demand'],
        'r': max(6, min(30, abs(item['gap']) // 5 + 6)),
        'label': item['node'].name,
        'quadrant': item['quadrant'],
    } for item in supply_demand[:25]])

    return render(request, 'pages/skill_intelligence.html', {
        'supply_demand': supply_demand,
        'top_gaps': top_gaps,
        'most_demanded': most_demanded,
        'oversupplied': oversupplied,
        'personal_gap': personal_gap,
        'industry_view': industry_view,
        'chart_labels': chart_labels,
        'chart_demand': chart_demand,
        'chart_supply': chart_supply,
        'chart_gap': chart_gap,
        'bubble_data': bubble_data,
        'role': role,
        'total_skills_tracked': len(supply_demand),
        'total_critical_gaps': sum(1 for s in supply_demand if s['quadrant'] == 'CRITICAL_GAP'),
    })


@login_required
def supply_demand_api(request):
    """JSON API for chart data refresh."""
    nodes = SkillNode.objects.filter(parent=None)
    result = []
    for node in nodes:
        demand = node.industry_demand_score
        supply = StudentSkillProfile.objects.filter(
            skill_node=node,
            proficiency__in=['INTERMEDIATE', 'ADVANCED', 'EXPERT']
        ).count()
        result.append({
            'skill': node.name,
            'demand': demand,
            'supply': supply,
            'gap': demand - supply,
        })
    return JsonResponse({'data': result})


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3 — INDUSTRY CHALLENGES → TALENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def challenges_view(request):
    """Challenge discovery page."""
    user = request.user
    role = user.primary_role

    qs = IndustryChallenge.objects.filter(is_verified=True, status='OPEN')

    q = request.GET.get('q', '').strip()
    difficulty = request.GET.get('difficulty', '')
    field_id = request.GET.get('field', '')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(organization_name__icontains=q) |
                       Q(description__icontains=q))
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    if field_id:
        qs = qs.filter(field_id=field_id)

    # Compute skill match for student
    challenges_data = []
    for ch in qs:
        if role == 'STUDENT':
            match_pct, matched, missing = _compute_skill_match(user, ch)
            registered = ChallengeParticipant.objects.filter(
                challenge=ch, student=user
            ).exists()
        else:
            match_pct, matched, missing = None, [], []
            registered = False
        challenges_data.append({
            'challenge': ch,
            'match_pct': match_pct,
            'matched': matched,
            'missing': missing,
            'registered': registered,
            'participant_count': ch.participant_count,
        })

    # Sort by match % for students
    if role == 'STUDENT':
        challenges_data.sort(key=lambda x: -(x['match_pct'] or 0))

    from apps.taxonomy.models import Field
    return render(request, 'pages/challenges.html', {
        'challenges_data': challenges_data,
        'role': role,
        'q': q,
        'difficulty': difficulty,
        'field_id': field_id,
        'difficulties': IndustryChallenge._meta.get_field('difficulty').choices,
        'fields': Field.objects.all().order_by('name'),
        'total': qs.count(),
    })


@login_required
def challenge_detail_view(request, slug):
    """Full challenge details + participate button."""
    challenge = get_object_or_404(IndustryChallenge, slug=slug, is_verified=True)
    user = request.user
    role = user.primary_role

    participant = None
    match_pct, matched, missing = None, [], []
    if role == 'STUDENT':
        participant = ChallengeParticipant.objects.filter(
            challenge=challenge, student=user
        ).first()
        match_pct, matched, missing = _compute_skill_match(user, challenge)

    submissions_count = challenge.submissions.count()
    participants_count = challenge.participants.count()

    return render(request, 'pages/challenge_detail.html', {
        'challenge': challenge,
        'participant': participant,
        'match_pct': match_pct,
        'matched': matched,
        'missing': missing,
        'role': role,
        'submissions_count': submissions_count,
        'participants_count': participants_count,
        'required_skills': challenge.required_skills.all(),
        'preferred_skills': challenge.preferred_skills.all(),
    })


@login_required
@require_POST
def participate_challenge_api(request):
    """Student registers for a challenge."""
    if request.user.primary_role != 'STUDENT':
        return JsonResponse({'success': False, 'error': 'Students only'}, status=403)

    data = json.loads(request.body)
    challenge_id = data.get('challenge_id')
    challenge = get_object_or_404(IndustryChallenge, id=challenge_id, is_verified=True)

    if not challenge.is_open:
        return JsonResponse({'success': False, 'error': 'Challenge is no longer open'})

    if challenge.participants.count() >= challenge.max_participants:
        return JsonResponse({'success': False, 'error': 'Challenge is full'})

    participant, created = ChallengeParticipant.objects.get_or_create(
        challenge=challenge, student=request.user
    )
    if not created:
        return JsonResponse({'success': False, 'error': 'Already registered'})

    _send_notification(
        request.user,
        f'Registered: {challenge.title}',
        f'You have successfully registered for "{challenge.title}" by {challenge.organization_name}. Deadline: {challenge.deadline.strftime("%d %b %Y")}.',
        link=f'/challenges/{challenge.slug}/'
    )
    return JsonResponse({'success': True, 'challenge_title': challenge.title})


@login_required
def my_challenges_view(request):
    """Student's active and past challenges."""
    if request.user.primary_role != 'STUDENT':
        return redirect('challenges')

    participations = ChallengeParticipant.objects.filter(
        student=request.user
    ).select_related('challenge').order_by('-registered_at')

    return render(request, 'pages/my_challenges.html', {
        'participations': participations,
        'stage_choices': ParticipantStage.choices,
    })


@login_required
def challenge_workspace_view(request, slug):
    """Student's personal workspace for a challenge."""
    challenge = get_object_or_404(IndustryChallenge, slug=slug)
    if request.user.primary_role != 'STUDENT':
        return redirect('challenge_detail', slug=slug)

    participant = get_object_or_404(
        ChallengeParticipant, challenge=challenge, student=request.user
    )
    tasks = ChallengeTask.objects.filter(participant=participant)
    submissions = ChallengeSubmission.objects.filter(participant=participant)
    team = ChallengeTeamMember.objects.filter(student=request.user).select_related('team').first()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_task':
            ChallengeTask.objects.create(
                challenge=challenge,
                participant=participant,
                title=request.POST.get('title', ''),
                description=request.POST.get('description', ''),
            )
        elif action == 'update_progress':
            participant.progress_pct = int(request.POST.get('progress', 0))
            participant.stage = 'IN_PROGRESS'
            participant.save()
        return redirect('challenge_workspace', slug=slug)

    return render(request, 'pages/challenge_workspace.html', {
        'challenge': challenge,
        'participant': participant,
        'tasks': tasks,
        'todo_tasks': tasks.filter(status='TODO'),
        'inprog_tasks': tasks.filter(status='IN_PROGRESS'),
        'done_tasks': tasks.filter(status='DONE'),
        'submissions': submissions,
        'team': team,
        'has_final_submission': submissions.filter(is_final=True).exists(),
    })


@login_required
@require_POST
def submit_challenge_api(request):
    """Student submits their project."""
    if request.user.primary_role != 'STUDENT':
        return JsonResponse({'success': False, 'error': 'Students only'}, status=403)

    data = json.loads(request.body)
    challenge_id = data.get('challenge_id')
    challenge = get_object_or_404(IndustryChallenge, id=challenge_id)
    participant = get_object_or_404(ChallengeParticipant, challenge=challenge, student=request.user)

    submission = ChallengeSubmission.objects.create(
        challenge=challenge,
        participant=participant,
        title=data.get('title', ''),
        description=data.get('description', ''),
        github_url=data.get('github_url', '') or None,
        demo_url=data.get('demo_url', '') or None,
        documentation_url=data.get('documentation_url', '') or None,
        is_final=data.get('is_final', False),
    )
    if submission.is_final:
        participant.stage = ParticipantStage.SUBMITTED
        participant.save()
        _send_notification(
            request.user,
            'Submission received!',
            f'Your final submission for "{challenge.title}" has been received.',
            link=f'/challenges/{challenge.slug}/workspace/'
        )
    return JsonResponse({'success': True, 'submission_id': str(submission.id)})


@login_required
def evaluate_challenge_view(request, slug):
    """Company evaluator scores submissions."""
    challenge = get_object_or_404(IndustryChallenge, slug=slug)
    if request.user.primary_role != 'INDUSTRY':
        return redirect('challenge_detail', slug=slug)

    if challenge.company_user != request.user:
        return redirect('challenges')

    submissions = ChallengeSubmission.objects.filter(
        challenge=challenge, is_final=True
    ).select_related('participant__student')

    submissions_data = []
    for sub in submissions:
        try:
            evaluation = sub.evaluation
        except SubmissionEvaluation.DoesNotExist:
            evaluation = None
        submissions_data.append({'submission': sub, 'evaluation': evaluation})

    return render(request, 'pages/challenge_evaluate.html', {
        'challenge': challenge,
        'submissions_data': submissions_data,
        'skill_nodes': challenge.required_skills.all(),
    })


@login_required
@require_POST
def save_evaluation_api(request):
    """Save evaluation scores for a submission."""
    if request.user.primary_role != 'INDUSTRY':
        return JsonResponse({'success': False, 'error': 'Industry users only'}, status=403)

    data = json.loads(request.body)
    submission_id = data.get('submission_id')
    submission = get_object_or_404(ChallengeSubmission, id=submission_id)

    if submission.challenge.company_user != request.user:
        return JsonResponse({'success': False, 'error': 'Not your challenge'}, status=403)

    eval_obj, _ = SubmissionEvaluation.objects.update_or_create(
        submission=submission,
        defaults={
            'evaluator': request.user,
            'technical_score': int(data.get('technical', 0)),
            'problem_score': int(data.get('problem', 0)),
            'innovation_score': int(data.get('innovation', 0)),
            'implementation_score': int(data.get('implementation', 0)),
            'documentation_score': int(data.get('documentation', 0)),
            'presentation_score': int(data.get('presentation', 0)),
            'feedback': data.get('feedback', ''),
        }
    )

    # Add verified skill evidence for student
    verified_node_ids = data.get('verified_skills', [])
    if verified_node_ids:
        from apps.genome.models import SkillNode
        nodes = SkillNode.objects.filter(id__in=verified_node_ids)
        eval_obj.skills_verified.set(nodes)
        student = submission.participant.student
        for node in nodes:
            ev, created = SkillEvidence.objects.get_or_create(
                student=student,
                skill_node=node,
                evidence_type='INDUSTRY_CHALLENGE',
                source_title=f'Industry Challenge: {submission.challenge.title}',
                defaults={
                    'score_percentage': eval_obj.total_score,
                    'verified_by': request.user,
                    'verified_at': timezone.now(),
                    'is_approved': True,
                }
            )
            profile = _get_or_create_profile(student, node)
            profile.recalculate()

    # Update participant stage
    participant = submission.participant
    participant.stage = ParticipantStage.EVALUATED
    participant.save()

    _send_notification(
        participant.student,
        'Your submission has been evaluated!',
        f'Score: {eval_obj.total_score}/100 for "{submission.challenge.title}". Check your results.',
        link=f'/challenges/{submission.challenge.slug}/'
    )
    return JsonResponse({'success': True, 'total_score': eval_obj.total_score})


@login_required
@require_POST
def update_pipeline_api(request):
    """Company moves a student through the talent pipeline."""
    if request.user.primary_role != 'INDUSTRY':
        return JsonResponse({'success': False, 'error': 'Industry only'}, status=403)

    data = json.loads(request.body)
    participant_id = data.get('participant_id')
    new_stage = data.get('stage')

    participant = get_object_or_404(ChallengeParticipant, id=participant_id)
    if participant.challenge.company_user != request.user:
        return JsonResponse({'success': False, 'error': 'Not your challenge'}, status=403)

    participant.stage = new_stage
    participant.save()

    stage_messages = {
        'SHORTLISTED': 'You have been shortlisted! 🎉',
        'INTERVIEW': 'You have been invited for an interview! Please check your email.',
        'INTERNSHIP': 'Congratulations! You have been offered an internship opportunity.',
        'JOB_OFFER': 'Congratulations! A job offer has been extended to you.',
    }
    msg = stage_messages.get(new_stage, f'Your application status has been updated to {new_stage}.')
    _send_notification(
        participant.student,
        f'Status update: {participant.challenge.title}',
        msg,
        link=f'/challenges/{participant.challenge.slug}/'
    )
    return JsonResponse({'success': True, 'new_stage': new_stage})


@login_required
def challenge_pipeline_view(request, slug):
    """Visual talent pipeline for company."""
    challenge = get_object_or_404(IndustryChallenge, slug=slug)
    if request.user.primary_role != 'INDUSTRY' or challenge.company_user != request.user:
        return redirect('challenge_detail', slug=slug)

    pipeline_data = {}
    for stage_key, stage_label in ParticipantStage.choices:
        participants = ChallengeParticipant.objects.filter(
            challenge=challenge, stage=stage_key
        ).select_related('student')
        pipeline_data[stage_key] = {
            'label': stage_label,
            'participants': participants,
            'count': participants.count(),
        }

    return render(request, 'pages/challenge_pipeline.html', {
        'challenge': challenge,
        'pipeline_data': pipeline_data,
        'stage_choices': ParticipantStage.choices,
        'total': challenge.participants.count(),
    })


@login_required
def create_challenge_view(request):
    """Company posts a new challenge."""
    if request.user.primary_role != 'INDUSTRY':
        return redirect('challenges')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        base_slug = slugify(title)
        slug = base_slug
        count = 1
        while IndustryChallenge.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{count}'
            count += 1

        import json as _json
        deadline_str = request.POST.get('deadline', '')
        from django.utils.dateparse import parse_datetime
        deadline = parse_datetime(deadline_str + ':00') or timezone.now() + timezone.timedelta(days=30)

        challenge = IndustryChallenge.objects.create(
            title=title,
            slug=slug,
            company_user=request.user,
            organization_name=request.user.organization_name or request.POST.get('org_name', ''),
            problem_statement=request.POST.get('problem_statement', ''),
            description=request.POST.get('description', ''),
            difficulty=request.POST.get('difficulty', 'INTERMEDIATE'),
            duration_weeks=int(request.POST.get('duration_weeks', 4)),
            team_min=int(request.POST.get('team_min', 1)),
            team_max=int(request.POST.get('team_max', 4)),
            deadline=deadline,
            rewards=request.POST.get('rewards', ''),
            opportunity_after=request.POST.get('opportunity_after', ''),
            is_team_challenge=request.POST.get('is_team', '') == 'on',
            max_participants=int(request.POST.get('max_participants', 500)),
        )

        # Required skills
        skill_ids = request.POST.getlist('required_skills')
        if skill_ids:
            nodes = SkillNode.objects.filter(id__in=skill_ids)
            challenge.required_skills.set(nodes)

        return redirect('challenge_detail', slug=challenge.slug)

    skill_nodes = SkillNode.objects.filter(parent=None).order_by('category', 'name')
    return render(request, 'pages/challenge_create.html', {
        'difficulty_choices': IndustryChallenge._meta.get_field('difficulty').choices,
        'skill_nodes': skill_nodes,
    })


@login_required
def challenges_admin_view(request):
    """Admin/institution overview of all challenges and outcomes."""
    role = request.user.primary_role
    if role not in ('SYSTEM_ADMIN', 'INSTITUTION', 'ACADEMICIAN'):
        return redirect('challenges')

    challenges = IndustryChallenge.objects.all().order_by('-created_at')
    total_participants = ChallengeParticipant.objects.count()
    total_submissions = ChallengeSubmission.objects.filter(is_final=True).count()
    total_evaluations = SubmissionEvaluation.objects.count()
    total_internships = ChallengeParticipant.objects.filter(stage='INTERNSHIP').count()
    total_jobs = ChallengeParticipant.objects.filter(stage='JOB_OFFER').count()

    return render(request, 'pages/challenges_admin.html', {
        'challenges': challenges,
        'total_participants': total_participants,
        'total_submissions': total_submissions,
        'total_evaluations': total_evaluations,
        'total_internships': total_internships,
        'total_jobs': total_jobs,
        'role': role,
    })
