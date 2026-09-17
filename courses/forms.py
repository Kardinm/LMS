from django import forms
from users.models import User
from .models import *


class CourseForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label='Теги курсу',
        help_text='Почніть вводити назву та оберіть підказку або додайте новий тег. Кілька тегів розділяйте комами.',
        widget=forms.TextInput(attrs={
            'placeholder': 'Наприклад: математика, алгебра',
            'autocomplete': 'off',
        }),
    )
    tag_icon = forms.ChoiceField(
        choices=CourseTag.ICON_CHOICES,
        label='Іконка для тегу',
        initial='📚',
        help_text='Застосовується лише до нових тегів, які ще не існують.',
    )

    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(self.instance.tags.values_list('name', flat=True))

    def save(self, commit=True):
        course = super().save(commit=commit)
        if commit:
            self._save_new_tags(course)
        else:
            original_save_m2m = self.save_m2m

            def save_m2m():
                original_save_m2m()
                self._save_new_tags(course)

            self.save_m2m = save_m2m
        return course

    def _save_new_tags(self, course):
        tags = []
        icon = self.cleaned_data.get('tag_icon', '📚')
        for name in self.cleaned_data.get('tags_input', '').split(','):
            name = name.strip()
            if name:
                tag, _ = CourseTag.objects.get_or_create(
                    name__iexact=name,
                    defaults={'name': name, 'icon': icon},
                )
                tags.append(tag)
        course.tags.set(tags)

    def clean_tags_input(self):
        names = []
        seen = set()
        for raw_name in self.cleaned_data['tags_input'].split(','):
            name = raw_name.strip()
            key = name.casefold()
            if name and key not in seen:
                if len(name) > 50:
                    raise forms.ValidationError('Назва тегу не може бути довшою за 50 символів.')
                names.append(name)
                seen.add(key)
        if len(names) > 10:
            raise forms.ValidationError('Можна додати не більше 10 тегів.')
        return ', '.join(names)

class CourseCreateForm(CourseForm):
    BADGE_ICON_CHOICES = [
        ('🏆', '🏆 Кубок'),
        ('🎓', '🎓 Академічна шапка'),
        ('🌟', '🌟 Зірка'),
        ('🏅', '🏅 Медаль'),
        ('🚀', '🚀 Ракета'),
        ('💎', '💎 Діамант'),
    ]
    completion_badge_icon = forms.ChoiceField(
        choices=BADGE_ICON_CHOICES,
        label='Емблема бейджика',
        initial='🏆',
    )

    class Meta(CourseForm.Meta):
        fields = CourseForm.Meta.fields + ['completion_badge_name', 'completion_badge_icon', 'completion_badge_color']
        widgets = {
            **CourseForm.Meta.widgets,
            'completion_badge_name': forms.TextInput(attrs={'placeholder': 'Наприклад, Майстер алгебри'}),
            'completion_badge_color': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'completion_badge_name': 'Назва бейджика за проходження',
            'completion_badge_color': 'Колір бейджика',
        }

    def clean_completion_badge_color(self):
        color = self.cleaned_data['completion_badge_color']
        if color and (len(color) != 7 or not color.startswith('#') or any(char not in '0123456789abcdefABCDEF#' for char in color)):
            raise forms.ValidationError('Вкажіть колір у форматі #RRGGBB.')
        return color


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
        fields = ['title', 'lesson_type', 'content', 'video_url', 'order']
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


class CourseSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Пошук',
        widget=forms.TextInput(attrs={'placeholder': 'Назва курсу...'})
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['teacher', 'admin']).order_by('username'),
        required=False,
        label='Викладач',
        empty_label='— Усі викладачі —'
    )
