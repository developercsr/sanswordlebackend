from django.contrib import admin
from .models import UserFavoriteWords


@admin.register(UserFavoriteWords)
class UserFavoriteWordsAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
