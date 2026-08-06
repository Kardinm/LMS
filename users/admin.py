from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    autocomplete_fields = ['course']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        ('Додаткові поля', {
            'fields': ('role', 'bio', 'avatar', 'birth_date'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткові поля', {
            'fields': ('role', 'email', 'first_name', 'last_name'),
        }),
    )

    inlines = [SubscriptionInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'subscribed_at']
    list_filter = ['course', 'subscribed_at']
    search_fields = ['student__username', 'course__title']
    autocomplete_fields = ['student', 'course']
