from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib import messages

from .models import Course, Module, Lesson, Assignment, Submission, Grade
from .forms import CourseForm, ModuleForm, LessonForm, AssignmentForm, SubmissionForm, GradeForm


class TeacherOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        return self.request.user.is_teacher() or self.request.user.is_admin_role()


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_courses'] = Course.objects.all()[:5]
        context['total_courses'] = Course.objects.count()
        return context


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'


class CourseCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Курс створено!')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Курс оновлено!')
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Курс видалено!')
        return super().delete(request, *args, **kwargs)




class ModuleCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
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


class ModuleUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    pk_url_kwarg = 'module_pk'

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Модуль оновлено!')
        return super().form_valid(form)


class ModuleDeleteView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'
    pk_url_kwarg = 'module_pk'

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Модуль видалено!')
        return super().delete(request, *args, **kwargs)





class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        module = lesson.module
        course = module.course

        lessons = list(module.lessons.all())
        idx = lessons.index(lesson)
        context['prev_lesson'] = lessons[idx - 1] if idx > 0 else None
        context['next_lesson'] = lessons[idx + 1] if idx < len(lessons) - 1 else None
        context['module'] = module
        context['course'] = course
        
        return context


class LessonCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    pk_url_kwarg = 'lesson_pk'

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
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


class LessonUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    pk_url_kwarg = 'lesson_pk'

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


class LessonDeleteView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'
    pk_url_kwarg = 'lesson_pk'

    def get_success_url(self):
        return self.object.module.course.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Урок видалено!')
        return super().delete(request, *args, **kwargs)
    



class AssignmentDetailView(DetailView):
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
        context['lesson'] = lesson
        context['module'] = module
        context['course'] = course

        if self.request.user.is_authenticated:
            try:
                context['my_submission'] = Submission.objects.get(
                    assignment=assignment, student=self.request.user
                )
            except Submission.DoesNotExist:
                context['my_submission'] = None

        return context


class AssignmentCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/assignment_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_pk'])
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


class AssignmentUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/assignment_form.html'
    pk_url_kwarg = 'assignment_pk'

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


class AssignmentDeleteView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'courses/assignment_confirm_delete.html'
    pk_url_kwarg = 'assignment_pk'

    def get_success_url(self):
        return self.object.lesson.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Завдання видалено!')
        return super().delete(request, *args, **kwargs)





class SubmissionCreateView(LoginRequiredMixin, CreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'courses/submission_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(Assignment, pk=self.kwargs['assignment_pk'])

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


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    model = Submission
    template_name = 'courses/submission_detail.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'submission_pk'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_student():
            qs = qs.filter(student=self.request.user)
            
        return qs


class GradeCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'courses/grade_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=self.kwargs['submission_pk'])
        
        if hasattr(self.submission, 'grade'):
            messages.warning(request, 'Ця відповідь вже оцінена. Ви можете оновити оцінку.')
            return redirect('grade_update', course_pk=self.kwargs['course_pk'],
                          module_pk=self.kwargs['module_pk'], lesson_pk=self.kwargs['lesson_pk'],
                          assignment_pk=self.kwargs['assignment_pk'],
                          submission_pk=self.submission.pk
            )
        
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


class GradeUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'courses/grade_form.html'
    pk_url_kwarg = 'grade_pk'

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



class TeacherDashboardView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, TemplateView):
    template_name = 'courses/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_admin_role():
            context['my_courses'] = Course.objects.all()
            context['total_students'] = user.__class__.objects.filter(role='student').count()
        else:
            context['my_courses'] = Course.objects.filter(author=user)
            
            context['total_students'] = Submission.objects.filter(
                assignment__lesson__module__course__in=context['my_courses']
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

        return context