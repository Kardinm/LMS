from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Викладач'),
        ('admin', 'Адміністратор'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Роль'
    )
    bio = models.TextField(blank=True, verbose_name='Про себе')
    avatar = models.FileField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата народження')

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_admin_role(self):
        return self.role == 'admin'
