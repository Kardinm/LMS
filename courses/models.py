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
    

class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Модуль'
    )
    title = models.CharField(max_length=255, verbose_name='Назва уроку')
    content = models.TextField(blank=True, verbose_name='Текстовий контент')
    video_url = models.URLField(blank=True, verbose_name='Посилання на відео')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return f"{self.order}. {self.title}"

    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={
            'course_pk': self.module.course.pk,
            'module_pk': self.module.pk,
            'lesson_pk': self.pk
        })


class Assignment(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Урок'
    )
    title = models.CharField(max_length=255, verbose_name='Назва завдання')
    description = models.TextField(blank=True, verbose_name='Опис завдання')
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн')
    max_score = models.PositiveIntegerField(default=100, verbose_name='Максимальний бал')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Завдання'
        verbose_name_plural = 'Завдання'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('assignment_detail', kwargs={
            'course_pk': self.lesson.module.course.pk,
            'module_pk': self.lesson.module.pk,
            'lesson_pk': self.lesson.pk,
            'assignment_pk': self.pk,
        })


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Завдання'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Студент'
    )
    text = models.TextField(blank=True, verbose_name='Текстова відповідь')
    file = models.FileField(upload_to='submissions/', blank=True, null=True, verbose_name='Файл')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата здачі')

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Відповідь'
        verbose_name_plural = 'Відповіді'
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f'Відповідь {self.student.username} на {self.assignment.title}'