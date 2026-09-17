from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Lesson, Submission


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


@login_required
@require_GET
def lesson_file(request, filename):
    lesson = get_object_or_404(
        Lesson.objects.filter(
            Q(module__course__author=request.user) |
            Q(module__course__subscriptions__student=request.user)
        ).distinct(),
        file=f'lesson_materials/{filename}',
    )
    try:
        file = lesson.file.open('rb')
    except FileNotFoundError:
        raise Http404('Файл не знайдено.')
    return FileResponse(file, as_attachment=True, filename=Path(filename).name)