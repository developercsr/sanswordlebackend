"""
Admin configuration for User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role display."""
    list_display = ['email', 'full_name', 'role', 'status', 'created_by', 'deactivated_by', 'deactivated_at', 'created_at']

    @admin.display(description='Status')
    def status(self, obj):
        return 'active' if obj.is_active else 'inactive'
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    filter_horizontal = []
    raw_id_fields = ['created_by', 'deactivated_by']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'mobile_number', 'school', 'role', 'created_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Deactivation', {'fields': ('deactivated_by', 'deactivated_at')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role'),
        }),
    )
