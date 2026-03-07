"""
Role-based access control with hierarchy.
Hierarchy: admin > word_manager > word_checker > word_uploader.
Higher level users can CRUD lower level users.
"""
from rest_framework import permissions

from .hierarchy import can_manage, get_role_level


class IsAdmin(permissions.BasePermission):
    """Full access - admin role only."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsWordManager(permissions.BasePermission):
    """Word Manager and above can manage words."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'word_manager')


class IsWordChecker(permissions.BasePermission):
    """Word Checker and above can verify words."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'admin', 'word_manager', 'word_checker'
        )


class IsWordUploader(permissions.BasePermission):
    """Word Uploader and above can upload words."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_role_level(request.user.role) >= 1


class CanManageUsers(permissions.BasePermission):
    """
    User can manage (list/create/update/delete) only users with lower hierarchy level.
    Admin > word_manager > word_checker > word_uploader.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_role_level(request.user.role) >= 2
