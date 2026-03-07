"""
Sanskrit Word model with auto-calculated length.
"""
from django.db import models
from django.conf import settings


class Word(models.Model):
    """
    Sanskrit word with meaning, hints, and verification workflow.
    Length is automatically calculated from the word.
    """
    word = models.CharField(max_length=255)
    meaning = models.TextField(blank=True)
    hint1 = models.CharField(max_length=255, blank=True)
    hint2 = models.CharField(max_length=255, blank=True)
    length = models.PositiveIntegerField(default=0, editable=False)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_words'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_words'
    )
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'words_word'
        verbose_name = 'Word'
        verbose_name_plural = 'Words'
        ordering = ['-created_at']

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        """Auto-calculate length from the word before saving."""
        self.length = len(self.word) if self.word else 0
        super().save(*args, **kwargs)
