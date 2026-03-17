"""
UserFavoriteWords model - one row per user, stores nested JSON.
"""
from django.db import models
from django.conf import settings


class UserFavoriteWords(models.Model):
    """One row per user. favorite_data: {class_X: {chapter_Y: {length: [word_ids]}}}"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_words'
    )
    favorite_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'favorites_userfavoritewords'
