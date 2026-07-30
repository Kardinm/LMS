from django.contrib import admin
from .models import *


class GradeInline(admin.StackedInline):
    model = Grade
    extra = 0
    readonly_fields = ['graded_at', 'graded_by']


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['student', 'submitted_at']
    fields = ['student', 'text', 'file', 'submitted_at']


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1
    fields = ['title', 'deadline', 'max_score']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'video_url']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'description']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'created_at']
    list_filter = ['module__course', 'module']
    search_fields = ['title', 'content']
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'deadline', 'max_score', 'created_at']
    list_filter = ['lesson__module__course', 'lesson__module']
    search_fields = ['title', 'description']
    inlines = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at']
    list_filter = ['assignment__lesson__module__course', 'submitted_at']
    search_fields = ['student__username', 'text']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['submission', 'score', 'graded_by', 'graded_at']
    list_filter = ['graded_at', 'graded_by']
    search_fields = ['submission__student__username', 'comment']
