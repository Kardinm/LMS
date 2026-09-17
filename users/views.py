from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F
from .forms import UserRegisterForm, UserUpdateForm
from .models import User


def get_profile_badges(profile_user):
    """Return earned profile titles and course-completion badges."""
    from courses.models import CourseCompletion, Grade

    badges = []
    subscriptions = profile_user.subscriptions.count()
    submissions = profile_user.submissions.filter(grade__isnull=False).count()
    excellent_grades = Grade.objects.filter(
        submission__student=profile_user,
        score__gte=F('submission__assignment__max_score') * 0.9,
    ).count()

    if subscriptions >= 5:
        badges.append({'name': 'Допитливий учень', 'icon': '📚', 'color': '#2563eb', 'description': 'Підписка на 5 або більше курсів'})
    if submissions >= 10:
        badges.append({'name': 'Наполегливий учень', 'icon': '✍️', 'color': '#059669', 'description': 'Виконано 10 або більше завдань'})
    if excellent_grades >= 5:
        badges.append({'name': 'Відмінник', 'icon': '🌟', 'color': '#d97706', 'description': 'Отримано 5 високих оцінок'})

    if profile_user.is_teacher() or profile_user.is_admin_role():
        followers = profile_user.courses.filter(subscriptions__isnull=False).values('subscriptions__student').distinct().count()
        if followers >= 10:
            badges.append({'name': 'Популярний викладач', 'icon': '🎓', 'color': '#7c3aed', 'description': '10 або більше учнів на курсах'})
        if followers >= 50:
            badges.append({'name': 'Улюблений викладач', 'icon': '🏅', 'color': '#db2777', 'description': '50 або більше учнів на курсах'})

    completion_badges = []
    completions = CourseCompletion.objects.filter(student=profile_user).select_related('course')
    for completion in completions:
        course = completion.course
        if course.completion_badge_name:
            completion_badges.append({
                'name': course.completion_badge_name,
                'icon': course.completion_badge_icon or '🏆',
                'color': course.completion_badge_color or '#6c63ff',
                'description': f'Курс «{course.title}» завершено',
            })
    return badges, completion_badges


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Реєстрація пройшла успішно!')
        return response


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    badges, completion_badges = get_profile_badges(request.user)
    return render(request, 'users/profile.html', {
        'form': form,
        'profile_user': request.user,
        'badges': badges,
        'completion_badges': completion_badges,
    })


class PublicProfileView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'users/public_profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        badges, completion_badges = get_profile_badges(self.object)
        context['badges'] = badges
        context['completion_badges'] = completion_badges
        context['authored_courses'] = self.object.courses.all().prefetch_related('tags')
        return context
