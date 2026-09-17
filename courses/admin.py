from django.contrib import admin
from .models import *


class OwnedContentAdmin(admin.ModelAdmin):
    owner_path = 'author'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(**{self.owner_path: request.user})

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and (obj is None or self.get_queryset(request).filter(pk=obj.pk).exists())

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) and (obj is None or self.get_queryset(request).filter(pk=obj.pk).exists())

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) and (obj is None or self.get_queryset(request).filter(pk=obj.pk).exists())

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        paths = {Course: 'author', Module: 'course__author', Lesson: 'module__course__author',
                 Assignment: 'lesson__module__course__author', Submission: 'assignment__lesson__module__course__author'}
        model = db_field.remote_field.model
        if model in paths:
            kwargs['queryset'] = model.objects.filter(**{paths[model]: request.user})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



class GradeInline(admin.StackedInline):
    model = Grade
    extra = 0
    readonly_fields = ['graded_at', 'graded_by']


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['student', 'submitted_at']
    fields = ['student', 'text', 'file', 'submitted_at']
    show_change_link = True


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1
    fields = ['title', 'deadline', 'max_score']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'lesson_type', 'video_url']


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'order']


@admin.register(Course)
class CourseAdmin(OwnedContentAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author', 'tags']
    filter_horizontal = ['tags']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]

    def get_readonly_fields(self, request, obj=None):
        fields = ['author']
        if obj:
            fields += ['completion_badge_name', 'completion_badge_icon', 'completion_badge_color']
        return fields

    def get_form(self, request, obj=None, **kwargs):
        from .forms import CourseCreateForm, CourseForm
        kwargs['form'] = CourseForm if obj else CourseCreateForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)




@admin.register(Module)
class ModuleAdmin(OwnedContentAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'description']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(OwnedContentAdmin):
    owner_path = 'module__course__author'
    list_display = ['title', 'module', 'lesson_type', 'order', 'created_at']
    list_filter = ['module__course', 'module']
    search_fields = ['title', 'content']
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(OwnedContentAdmin):
    owner_path = 'lesson__module__course__author'
    list_display = ['title', 'lesson', 'deadline', 'max_score', 'created_at']
    list_filter = ['lesson__module__course', 'lesson__module']
    search_fields = ['title', 'description']


@admin.register(Submission)
class SubmissionAdmin(OwnedContentAdmin):
    owner_path = 'assignment__lesson__module__course__author'
    list_display = ['student', 'assignment', 'submitted_at']
    list_filter = ['assignment__lesson__module__course', 'submitted_at']
    search_fields = ['student__username', 'text']
    readonly_fields = ['student', 'assignment', 'text', 'file', 'submitted_at']

    def has_add_permission(self, request):
        return False


@admin.register(Grade)
class GradeAdmin(OwnedContentAdmin):
    readonly_fields = ['graded_by']

    def save_model(self, request, obj, form, change):
        obj.graded_by = request.user
        super().save_model(request, obj, form, change)

    owner_path = 'submission__assignment__lesson__module__course__author'
    list_display = ['submission', 'score', 'graded_by', 'graded_at']
    list_filter = ['graded_at', 'graded_by']
    search_fields = ['submission__student__username', 'comment']


@admin.register(CourseTag)
class CourseTagAdmin(admin.ModelAdmin):
    search_fields = ['name']
