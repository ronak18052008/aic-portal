from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.sources.models import Source, VerificationRecord, SourceConflict

@login_required
def sources_provenance_view(request):
    sources = Source.objects.all()
    records = VerificationRecord.objects.all()[:20]
    conflicts = SourceConflict.objects.all()[:10]
    
    context = {
        'sources': sources,
        'records': records,
        'conflicts': conflicts,
    }
    return render(request, 'pages/sources_provenance.html', context)
