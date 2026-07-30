from django.urls import path

from .views import *


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

    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/add/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/edit/', AssignmentUpdateView.as_view(), name='assignment_update'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
    
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/submit/', SubmissionCreateView.as_view(), name='submission_create'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/submission/<int:submission_pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/submission/<int:submission_pk>/grade/', GradeCreateView.as_view(), name='grade_create'),
    path('<int:course_pk>/module/<int:module_pk>/lesson/<int:lesson_pk>/assignment/<int:assignment_pk>/submission/<int:submission_pk>/grade/edit/', GradeUpdateView.as_view(), name='grade_update'),
    
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    
    path('<int:pk>/submissions/', CourseSubmissionsView.as_view(), name='course_submissions'),
]
