from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Назва курсу')
    description = models.TextField(blank=True, verbose_name='Опис')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    tags = models.ManyToManyField('CourseTag', verbose_name='Теги', blank=True, related_name='courses')
    completion_badge_name = models.CharField('Назва бейджика', max_length=80, blank=True)
    completion_badge_icon = models.CharField('Емблема бейджика', max_length=8, blank=True, default='🏆')
    completion_badge_color = models.CharField('Колір бейджика', max_length=7, blank=True, default='#6c63ff')


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})

    def is_subscribed(self, user):
        if not user.is_authenticated:
            return False
        
        return self.subscriptions.filter(student=user).exists()


class CourseTag(models.Model):
    ICON_CHOICES = [('📚', '📚 Книги'), 
                    ('💻', '💻 Програмування'),
                    ('🔢', '🔢 Математика'), 
                    ('🌍', '🌍 Світ'),
                    ('🎨', '🎨 Мистецтво'), 
                    ('🔬', '🔬 Наука')]
    icon = models.CharField('Іконка', max_length=8, choices=ICON_CHOICES, default='📚')
    normalized_name = models.CharField(max_length=100, unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.name = ' '.join(self.name.split())
        self.normalized_name = self.name.casefold()
        super().save(*args, **kwargs)

    name = models.CharField('Назва тегу', max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег курсу'
        verbose_name_plural = 'Теги курсів'

    def __str__(self):
        return self.name


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
    LESSON_TYPE_CHOICES = [
        ('self_study', 'Самовивчення'),
        ('video', 'Відеоурок'),
        ('mixed', 'Змішаний'),
        ('live', 'Онлайн-зустріч'),
        ('practice', 'Практика'),
    ]

    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='self_study', verbose_name='Тип уроку')
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Модуль'
    )
    title = models.CharField(max_length=255, verbose_name='Назва уроку')
    content = models.TextField(blank=True, verbose_name='Текстовий контент')
    video_url = models.URLField(blank=True, verbose_name='Посилання на відео')
    file = models.FileField(
        upload_to='lesson_materials/', blank=True, verbose_name='Файл уроку',
        help_text='Необов’язково. Додайте конспект, презентацію, архів або інший навчальний матеріал.',
    )
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
    max_score = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)], verbose_name='Максимальний бал')
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
        settings.AUTH_USER_MODEL,
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
        return f"Відповідь {self.student.username} на '{self.assignment.title}'"


class Grade(models.Model):
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='grade',
        verbose_name='Відповідь'
    )
    score = models.PositiveIntegerField(verbose_name='Бал')
    comment = models.TextField(blank=True, verbose_name='Коментар викладача')
    graded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оцінювання')
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grades_given',
        verbose_name='Оцінив'
    )

    def clean(self):
        super().clean()
        if self.submission_id and self.score is not None and self.score > self.submission.assignment.max_score:
            raise ValidationError({'score': 'Бал не може перевищувати максимальний бал завдання.'})

    class Meta:
        verbose_name = 'Оцінка'
        verbose_name_plural = 'Оцінки'

    def __str__(self):
        return f"{self.score}/{self.submission.assignment.max_score} — {self.submission.student.username}"


class CourseCompletion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='completions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_completions')
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='confirmed_completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['course', 'student'], name='unique_course_completion')]
        verbose_name = 'Завершення курсу'
        verbose_name_plural = 'Завершення курсів'