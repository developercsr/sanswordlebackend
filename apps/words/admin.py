"""
Admin configuration for Word model.
"""
from django.contrib import admin
from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Word admin with filters and search."""
    list_display = ['word', 'length', 'meaning', 'is_verified', 'uploaded_by', 'verified_by', 'verified_at', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['word', 'meaning']
    readonly_fields = ['length', 'verified_at', 'created_at', 'updated_at']
    raw_id_fields = ['uploaded_by', 'verified_by']
