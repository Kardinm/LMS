from django import forms
from .models import Course, Module, Lesson


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