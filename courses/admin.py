from django.contrib import admin
from .models import Course, Module, Lesson


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
