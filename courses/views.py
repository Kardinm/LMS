from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib import messages
from .models import Course, Module, Lesson
from .forms import CourseForm, ModuleForm, LessonForm


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
