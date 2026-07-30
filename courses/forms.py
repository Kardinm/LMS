from django import forms
from .models import *


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/...'}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Ваша відповідь...'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['score', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Коментар викладача...'}),
        }

    def __init__(self, *args, max_score=None, **kwargs):
        super().__init__(*args, **kwargs)
        if max_score:
            self.fields['score'].widget.attrs['max'] = max_score
            self.fields['score'].widget.attrs['min'] = 0