"""
Management command to create default admin user.
Runs automatically after migrations via post_migrate signal.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_ADMIN_EMAIL = 'dhiyotek@gmail.com'
DEFAULT_ADMIN_PASSWORD = 'Dhiyo@123'
DEFAULT_ADMIN_ROLE = 'admin'


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    if not User.objects.filter(email=DEFAULT_ADMIN_EMAIL).exists():
        User.objects.create_superuser(
            email=DEFAULT_ADMIN_EMAIL,
            password=DEFAULT_ADMIN_PASSWORD,
            full_name='Default Admin',
            role=DEFAULT_ADMIN_ROLE,
        )
        return True
    return False


class Command(BaseCommand):
    """Create default admin user: dhiyotek@gmail.com / Dhiyo@123"""

    help = 'Creates default admin user (dhiyotek@gmail.com) if not exists'

    def handle(self, *args, **options):
        if create_default_admin():
            self.stdout.write(self.style.SUCCESS('Default admin user created successfully.'))
        else:
            self.stdout.write('Default admin user already exists.')
