"""
Signals for users app - create default admin after migrations.
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .management.commands.create_default_admin import create_default_admin


@receiver(post_migrate)
def create_default_admin_on_migrate(sender, **kwargs):
    """Create default admin user after migrations run (e.g. first server start)."""
    if sender.name == 'apps.users':
        create_default_admin()
