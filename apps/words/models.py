"""
Sanskrit Word model with auto-calculated length.
CheckerAction tracks which user took which action on a word (approve/reject/remove/update+approve).
"""
from django.db import models
from django.conf import settings


class CheckerAction(models.Model):
    """Through model for Word.checked_by; stores action type and time."""
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('updated_and_approved', 'Updated and Approved'),
        ('rejected', 'Rejected'),
        ('removed_for_me', 'Removed For Me'),
    ]
    word = models.ForeignKey(
        'Word',
        on_delete=models.CASCADE,
        related_name='checker_actions',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='word_checker_actions',
    )
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    action_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'words_checker_action'
        unique_together = [['word', 'user']]
        ordering = ['-action_at']


class Word(models.Model):
    """
    Sanskrit word with meaning, hints, and verification workflow.
    Length is automatically calculated from the word.
    class_name and chapter store string representations of lists, e.g. "['5','6']".
    """
    word = models.CharField(max_length=255)
    meaning = models.TextField(blank=True)
    hint1 = models.CharField(max_length=255, blank=True)
    hint2 = models.CharField(max_length=255, blank=True)
    length = models.PositiveIntegerField(default=0, editable=False)
    class_name = models.TextField(blank=True, default="[]")
    chapter = models.TextField(blank=True, default="[]")
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
    is_rejected = models.BooleanField(default=False)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_words'
    )
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_words'
    )
    checked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CheckerAction',
        related_name='checked_words',
        blank=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_words',
    )
    assigned_time = models.DateTimeField(null=True, blank=True)
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
