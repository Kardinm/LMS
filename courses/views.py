from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib import messages
from .models import Course, Module
from .forms import CourseForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_role()


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


class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Курс створено!')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Курс оновлено!')
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Курс видалено!')
        return super().delete(request, *args, **kwargs)
