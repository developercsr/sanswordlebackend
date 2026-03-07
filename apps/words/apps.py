"""
Words app configuration.
"""
from django.apps import AppConfig


class WordsConfig(AppConfig):
    """Words application config."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.words'
    verbose_name = 'Words'
    label = 'words'
