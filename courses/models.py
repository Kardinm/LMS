from django.db import models
from django.urls import reverse
from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Назва курсу')
    description = models.TextField(blank=True, verbose_name='Опис')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Курс'
    )
    title = models.CharField(max_length=255, verbose_name='Назва модуля')
    description = models.TextField(blank=True, verbose_name='Опис')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модулі'

    def __str__(self):
        return f"{self.order}. {self.title}"
