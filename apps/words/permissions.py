"""
Permissions for Words app.
Re-exports from users app for consistency.
"""
from apps.users.permissions import IsWordManager, IsWordChecker, IsWordUploader
