from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Submission


@login_required
@require_GET
def submission_file(request, filename):
    submission = get_object_or_404(
        Submission.objects.filter(
            Q(student=request.user) |
            Q(assignment__lesson__module__course__author=request.user)
        ),
        file=f'submissions/{filename}',
    )
    try:
        file = submission.file.open('rb')
    except FileNotFoundError:
        raise Http404('Файл не знайдено.')
    return FileResponse(file, as_attachment=True, filename=Path(filename).name)