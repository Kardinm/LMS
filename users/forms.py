from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Ім'я користувача",
        help_text='До 150 символів. Використовуйте літери, цифри та символи @ . + - _.',
    )
    email = forms.EmailField(required=True, label='Електронна пошта')
    role = forms.ChoiceField(
        choices=[
            ('student', 'Студент'),
            ('teacher', 'Викладач'),
        ],
        label='Роль',
        widget=forms.Select
    )
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердження пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']
        labels = {
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
        }


class UserUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, label='Аватар')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'birth_date', 'avatar']
        labels = {
            'username': "Ім'я користувача",
            'email': 'Електронна пошта',
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'bio': 'Про себе',
            'birth_date': 'Дата народження',
            'avatar': 'Аватар',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
