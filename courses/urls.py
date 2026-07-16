from django.urls import path

from .views import (
    CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView,
    ModuleCreateView, ModuleUpdateView, ModuleDeleteView,
    LessonCreateView, LessonDetailView, LessonUpdateView, LessonDeleteView
)


urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),

    path('<int:course_pk>/module/add/', ModuleCreateView.as_view(), name='module_create'),
    path('<int:course_pk>/module/<int:module_pk>/edit/', ModuleUpdateView.as_view(), name='module_update'),
    path('<int:course_pk>/module/<int:module_pk>/delete/', ModuleDeleteView.as_view(), name='module_delete'),

    path('<int:course_pk>/module/<int:module_pk>/lesson/add/', LessonCreateView.as_view(), name='lesson_create'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/edit/', LessonUpdateView.as_view(), name='lesson_update'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),
]
