from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views import View
from django.db import transaction
from .models import CourseCompletion

from .models import Course, CourseTag, Module, Lesson, Assignment, Submission, Grade
from users.models import Subscription
from .forms import *


class NestedCourseMixin:
    def dispatch(self, request, *args, **kwargs):
        if 'course_pk' in kwargs:
            course = get_object_or_404(Course, pk=kwargs['course_pk'])
            if 'module_pk' in kwargs:
                module = get_object_or_404(Module, pk=kwargs['module_pk'], course=course)
            if 'lesson_pk' in kwargs:
                lesson = get_object_or_404(Lesson, pk=kwargs['lesson_pk'], module=module)
            if 'assignment_pk' in kwargs:
                assignment = get_object_or_404(Assignment, pk=kwargs['assignment_pk'], lesson=lesson)
            if 'submission_pk' in kwargs:
                get_object_or_404(Submission, pk=kwargs['submission_pk'], assignment=assignment)
        return super().dispatch(request, *args, **kwargs)


class TagCatalogMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_catalog'] = list(CourseTag.objects.values('name', 'icon'))
        return context

class TeacherOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        return self.request.user.is_teacher() or self.request.user.is_admin_role()


class CourseOwnerRequiredMixin(UserPassesTestMixin):
    owner_lookup = 'author'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_queryset(self):
        return super().get_queryset().filter(**{self.owner_lookup: self.request.user})


def is_course_owner(user, course):
    return user.is_authenticated and course.author_id == user.id


class SubscriptionRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        course_pk = self.kwargs.get('course_pk') or self.kwargs.get('pk')
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            return is_course_owner(user, course) or course.is_subscribed(user)
        
        return False


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_courses'] = Course.objects.all()[:5]
        context['total_courses'] = Course.objects.count()
        return context

# Курси
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        qs = Course.objects.select_related('author').prefetch_related('tags')
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(author__username__icontains=query))

        for param, field in [('author', 'author_id'), ('tag', 'tags__pk')]:
            value = self.request.GET.get(param)
            if value:
                if not value.isdecimal() or len(value) > 18:
                    return qs.none()
                qs = qs.filter(**{field: int(value)})
            
        return qs.distinct()

    def get_context_data(self, **kwargs):
        from users.models import User

        context = super().get_context_data(**kwargs)
        context.update(teachers=User.objects.filter(courses__isnull=False).distinct(),
                       tags=CourseTag.objects.all(), search_query=self.request.GET.get('q', ''),
                       selected_author=self.request.GET.get('author', ''),
                       selected_tag=self.request.GET.get('tag', ''))
        params = self.request.GET.copy()
        params.pop('page', None)
        context['get_params'] = params.urlencode()

        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        context['is_subscribed'] = course.is_subscribed(user)
        context['is_owner'] = is_course_owner(user, course)

        if context['is_owner']:
            context['subscribed_students'] = course.subscriptions.select_related('student').all()
            context['completed_student_ids'] = set(course.completions.values_list('student_id', flat=True))

        return context


class CourseCreateView(TagCatalogMixin, LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseCreateForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Курс створено!')
        return super().form_valid(form)


class CourseUpdateView(TagCatalogMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Курс оновлено!')
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Курс видалено!')
        return super().form_valid(form)


class CourseSubscribeView(LoginRequiredMixin, CreateView):
    template_name = 'courses/course_subscribe.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if not request.user.is_student():
            messages.error(request, 'Тільки студенти можуть підписуватися на курси.')
            return redirect(self.course.get_absolute_url())
        
        if self.course.is_subscribed(request.user):
            messages.info(request, 'Ви вже підписані на цей курс.')
            return redirect(self.course.get_absolute_url())
        
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        Subscription.objects.get_or_create(student=request.user, course=self.course)
        messages.success(request, f'Ви підписалися на курс "{self.course.title}"!')
        return redirect(self.course.get_absolute_url())

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'course': self.course})


class CourseUnsubscribeView(LoginRequiredMixin, CreateView):
    template_name = 'courses/course_unsubscribe.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if not request.user.is_student():
            messages.error(request, 'Тільки студенти можуть відписуватися від курсів.')
            return redirect(self.course.get_absolute_url())
        
        if not self.course.is_subscribed(request.user):
            messages.info(request, 'Ви не підписані на цей курс.')
            return redirect(self.course.get_absolute_url())
        
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        Subscription.objects.filter(student=request.user, course=self.course).delete()
        messages.success(request, f'Ви відписалися від курсу "{self.course.title}".')
        return redirect(self.course.get_absolute_url())

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'course': self.course})


# модулі
class ModuleCreateView(NestedCourseMixin, LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        if not is_course_owner(request.user, self.course):
            return HttpResponseForbidden('Лише автор курсу може змінювати його вміст.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        messages.success(self.request, 'Модуль додано!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.course.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context


class ModuleUpdateView(NestedCourseMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    pk_url_kwarg = 'module_pk'
    owner_lookup = 'course__author'

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Модуль оновлено!')
        return super().form_valid(form)


class ModuleDeleteView(NestedCourseMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'
    pk_url_kwarg = 'module_pk'
    owner_lookup = 'course__author'

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Модуль видалено!')
        return super().form_valid(form)


#уроки
class LessonDetailView(NestedCourseMixin, SubscriptionRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        module = lesson.module
        course = module.course
        user = self.request.user

        lessons = list(module.lessons.all())
        idx = lessons.index(lesson)
        context['prev_lesson'] = lessons[idx - 1] if idx > 0 else None
        context['next_lesson'] = lessons[idx + 1] if idx < len(lessons) - 1 else None
        context['module'] = module
        context['course'] = course
        context['is_owner'] = is_course_owner(user, course)

        if user.is_authenticated and user.is_student():
            context['user_submissions'] = Submission.objects.filter(
                assignment__lesson=lesson,
                student=user
            ).select_related('assignment', 'grade')

            total_assignments = Assignment.objects.filter(lesson__module=module).count()
            graded_submissions = Submission.objects.filter(
                assignment__lesson__module=module,
                student=user,
                grade__isnull=False
            ).count()
            context['module_progress'] = {
                'total': total_assignments,
                'done': graded_submissions,
                'percent': round((graded_submissions / total_assignments * 100), 1) if total_assignments > 0 else 0,
            }

        return context


class LessonCreateView(NestedCourseMixin,LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        if not is_course_owner(request.user, self.module.course):
            return HttpResponseForbidden('Лише автор курсу може змінювати його вміст.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.module = self.module
        messages.success(self.request, 'Урок створено!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.module
        context['course'] = self.module.course
        return context


class LessonUpdateView(NestedCourseMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    pk_url_kwarg = 'lesson_pk'
    owner_lookup = 'module__course__author'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Урок оновлено!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.object.module
        context['course'] = self.object.module.course
        return context


class LessonDeleteView(NestedCourseMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'
    pk_url_kwarg = 'lesson_pk'
    owner_lookup = 'module__course__author'

    def get_success_url(self):
        return self.object.module.course.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Урок видалено!')
        return super().form_valid(form)


#завдання
class AssignmentDetailView(NestedCourseMixin, SubscriptionRequiredMixin, DetailView):
    model = Assignment
    template_name = 'courses/assignment_detail.html'
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignment_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        lesson = assignment.lesson
        module = lesson.module
        course = module.course
        user = self.request.user

        context['lesson'] = lesson
        context['module'] = module
        context['course'] = course
        context['is_owner'] = is_course_owner(user, course)

        if user.is_authenticated:
            try:
                context['my_submission'] = Submission.objects.get(
                    assignment=assignment, student=user
                )
            except Submission.DoesNotExist:
                context['my_submission'] = None

        if is_course_owner(user, course):
            context['all_submissions'] = Submission.objects.filter(
                assignment=assignment
            ).select_related('student').prefetch_related('grade')

        return context


class AssignmentCreateView(NestedCourseMixin, LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/assignment_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
        if not is_course_owner(request.user, self.lesson.module.course):
            return HttpResponseForbidden('Лише автор курсу може змінювати його вміст.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.lesson = self.lesson
        messages.success(self.request, 'Завдання створено!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.lesson
        context['module'] = self.lesson.module
        context['course'] = self.lesson.module.course
        return context


class AssignmentUpdateView(NestedCourseMixin, LoginRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/assignment_form.html'
    pk_url_kwarg = 'assignment_pk'
    owner_lookup = 'lesson__module__course__author'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Завдання оновлено!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.object.lesson
        context['module'] = self.object.lesson.module
        context['course'] = self.object.lesson.module.course
        return context


class AssignmentDeleteView(NestedCourseMixin,LoginRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'courses/assignment_confirm_delete.html'
    pk_url_kwarg = 'assignment_pk'
    owner_lookup = 'lesson__module__course__author'

    def get_success_url(self):
        return self.object.lesson.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Завдання видалено!')
        return super().form_valid(form)


#відповіді
class SubmissionCreateView(NestedCourseMixin, LoginRequiredMixin, SubscriptionRequiredMixin, CreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'courses/submission_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.assignment = get_object_or_404(Assignment, pk=self.kwargs['assignment_pk'])
        if not request.user.is_student() or not self.assignment.lesson.module.course.is_subscribed(request.user):
            return HttpResponseForbidden('Здавати завдання можуть лише підписані студенти.')
        if Submission.objects.filter(assignment=self.assignment, student=request.user).exists():
            messages.warning(request, 'Ви вже здали це завдання.')
            return redirect(self.assignment.get_absolute_url())
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.assignment = self.assignment
        form.instance.student = self.request.user
        messages.success(self.request, 'Відповідь відправлено!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.assignment.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.assignment
        context['lesson'] = self.assignment.lesson
        context['module'] = self.assignment.lesson.module
        context['course'] = self.assignment.lesson.module.course
        return context


class SubmissionDetailView(NestedCourseMixin,LoginRequiredMixin, DetailView):
    model = Submission
    template_name = 'courses/submission_detail.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'submission_pk'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(student=self.request.user) | Q(assignment__lesson__module__course__author=self.request.user))

        return qs


#оцінки
class GradeCreateView(NestedCourseMixin, LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'courses/grade_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.submission = get_object_or_404(Submission, pk=self.kwargs['submission_pk'])
        if self.submission.assignment.lesson.module.course.author != request.user:
            return HttpResponseForbidden('Ви не автор цього курсу.')
        if hasattr(self.submission, 'grade'):
            messages.warning(request, 'Ця відповідь вже оцінена. Ви можете оновити оцінку.')
            return redirect('grade_update', course_pk=self.kwargs['course_pk'],
                          module_pk=self.kwargs['module_pk'], lesson_pk=self.kwargs['lesson_pk'],
                          assignment_pk=self.kwargs['assignment_pk'],
                          submission_pk=self.submission.pk)
        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['max_score'] = self.submission.assignment.max_score
        return kwargs

    def form_valid(self, form):
        form.instance.submission = self.submission
        form.instance.graded_by = self.request.user
        messages.success(self.request, 'Оцінку виставлено!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.submission.assignment.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.submission
        context['assignment'] = self.submission.assignment
        context['lesson'] = self.submission.assignment.lesson
        context['module'] = self.submission.assignment.lesson.module
        context['course'] = self.submission.assignment.lesson.module.course
        return context


class GradeUpdateView(NestedCourseMixin, LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'courses/grade_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Grade, submission_id=self.kwargs['submission_pk'])

    def dispatch(self, request, *args, **kwargs):
        grade = self.get_object()
        if grade.submission.assignment.lesson.module.course.author != request.user:
            return HttpResponseForbidden('Ви не автор цього курсу.')
        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['max_score'] = self.object.submission.assignment.max_score
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Оцінку оновлено!')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.submission.assignment.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.object.submission
        context['assignment'] = self.object.submission.assignment
        context['lesson'] = self.object.submission.assignment.lesson
        context['module'] = self.object.submission.assignment.lesson.module
        context['course'] = self.object.submission.assignment.lesson.module.course
        context['is_update'] = True
        return context


class CourseCompletionMarkView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk, student_pk):
        course = get_object_or_404(Course.objects.select_for_update(), pk=pk, author=request.user)
        subscription = get_object_or_404(Subscription, course=course, student_id=student_pk)
        assignments = Assignment.objects.filter(lesson__module__course=course)
        done = Submission.objects.filter(assignment__in=assignments, student=subscription.student, grade__isnull=False).count()
        if not assignments.exists() or done != assignments.count():
            messages.error(request, 'Спочатку учень має здати всі завдання курсу, а викладач — оцінити їх.')
        else:
            CourseCompletion.objects.get_or_create(course=course, student=subscription.student, defaults={'confirmed_by': request.user})
            messages.success(request, 'Проходження курсу підтверджено. Бейджик доступний у профілі учня.')
        return redirect(course)


class CourseCompletionRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk, student_pk):
        course = get_object_or_404(Course, pk=pk, author=request.user)
        CourseCompletion.objects.filter(course=course, student_id=student_pk).delete()
        messages.success(request, 'Підтвердження проходження скасовано.')
        return redirect(course)

#дашборд вчителя
class TeacherDashboardView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, TemplateView):
    template_name = 'courses/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['my_courses'] = Course.objects.filter(author=user)

        context['total_students'] = Subscription.objects.filter(
            course__in=context['my_courses']
        ).values('student').distinct().count()

        context['pending_submissions'] = Submission.objects.filter(
            assignment__lesson__module__course__in=context['my_courses'],
            grade__isnull=True
        ).select_related('student', 'assignment').order_by('submitted_at')

        context['total_submissions'] = Submission.objects.filter(
            assignment__lesson__module__course__in=context['my_courses']
        ).count()

        context['graded_submissions'] = Grade.objects.filter(
            submission__assignment__lesson__module__course__in=context['my_courses']
        ).count()

        return context


class CourseSubmissionsView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_submissions.html'
    context_object_name = 'course'

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if course.author != request.user:
            return HttpResponseForbidden('Ви не автор цього курсу.')
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        context['submissions'] = Submission.objects.filter(
            assignment__lesson__module__course=course
        ).select_related('student', 'assignment', 'assignment__lesson').prefetch_related('grade')

        context['total_submissions'] = context['submissions'].count()
        context['graded_count'] = Grade.objects.filter(
            submission__assignment__lesson__module__course=course
        ).count()
        context['pending_count'] = context['total_submissions'] - context['graded_count']

        context['subscribed_students'] = Subscription.objects.filter(
            course=course
        ).select_related('student')

        return context


#дашборд учня
class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'courses/student_dashboard.html'

    def test_func(self):
        return self.request.user.is_student()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['subscribed_courses'] = Course.objects.filter(
            subscriptions__student=user
        ).prefetch_related('subscriptions')

        context['my_submissions'] = Submission.objects.filter(
            student=user
        ).select_related('assignment', 'assignment__lesson', 'assignment__lesson__module', 'grade')

        grades = Grade.objects.filter(submission__student=user)
        if grades.exists():
            total_score = sum(g.score for g in grades)
            total_max = sum(g.submission.assignment.max_score for g in grades)
            context['average_score'] = round((total_score / total_max * 100), 1) if total_max > 0 else 0
            context['graded_count'] = grades.count()
        else:
            context['average_score'] = None
            context['graded_count'] = 0

        course_progress = []
        for course in context['subscribed_courses']:
            total_assignments = Assignment.objects.filter(
                lesson__module__course=course
            ).count()
            done_assignments = Submission.objects.filter(
                assignment__lesson__module__course=course,
                student=user,
                grade__isnull=False
            ).count()
            course_progress.append({
                'course': course,
                'total': total_assignments,
                'done': done_assignments,
                'percent': round((done_assignments / total_assignments * 100), 1) if total_assignments > 0 else 0,
            })
        context['course_progress'] = course_progress

        return context
