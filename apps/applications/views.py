from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.applications.models import Application, ApplicationStatus
from apps.opportunities.models import Opportunity

@login_required
def applications_list_view(request):
    status_filter = request.GET.get('status', '')
    applications = Application.objects.filter(applicant=request.user)
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': ApplicationStatus.choices,
        'total_count': applications.count(),
    }
    return render(request, 'pages/applications_list.html', context)

def apply_opportunity_view(request, opportunity_id):
    """View opportunity details and apply. Works for both logged-in and guest users."""
    opp = get_object_or_404(Opportunity, id=opportunity_id)
    
    applied = False
    if request.user.is_authenticated and request.method == 'POST':
        cover_note = request.POST.get('cover_note', '')
        app, created = Application.objects.get_or_create(
            applicant=request.user,
            opportunity=opp,
            defaults={
                'cover_note': cover_note,
                'status': ApplicationStatus.APPLIED,
                'is_external_redirect': False,
                'official_redirect_url': opp.official_apply_url
            }
        )

        from apps.notifications.models import Notification
        # Notify applicant
        Notification.objects.create(
            recipient=request.user,
            title=f"Application Submitted: {opp.title}",
            message=f"You successfully applied for {opp.title} at {opp.organization_name}. Track its progress on your applications dashboard.",
            notification_type='APPLICATION',
            link='/applications/'
        )

        # Notify recruiter / organization members
        from apps.accounts.models import User, PrimaryRole
        recruiters = User.objects.filter(
            primary_role=PrimaryRole.INDUSTRY,
            organization_name__icontains=opp.organization_name
        )
        for rec in recruiters:
            Notification.objects.create(
                recipient=rec,
                title=f"New Candidate Application: {opp.title}",
                message=f"{request.user.get_full_name()} submitted an application for {opp.title}. Evaluate their skill fit in ATS.",
                notification_type='APPLICATION',
                link=f"/applications/manage/?q={request.user.email}"
            )

        return redirect('applications_list')
    
    if request.user.is_authenticated:
        applied = Application.objects.filter(applicant=request.user, opportunity=opp).exists()

    required_skills = opp.required_skills.all()
    
    context = {
        'opportunity': opp,
        'applied': applied,
        'required_skills': required_skills,
    }
    return render(request, 'pages/apply_confirm.html', context)
