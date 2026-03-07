"""
User CRUD views - hierarchy-based.
Higher level users can manage (list/create/update/remove) lower level users.
Remove = soft delete (status inactive, deactivated_by set).
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from apps.users.permissions import CanManageUsers
from apps.users.hierarchy import can_manage, get_role_level, ROLE_LEVEL
from core.utils import success_response

User = get_user_model()


def _managed_users(request):
    """Users the requester can manage (lower hierarchy level only)."""
    requester_level = get_role_level(request.user.role)
    lower_roles = [r for r, lvl in ROLE_LEVEL.items() if lvl < requester_level]
    return User.objects.filter(role__in=lower_roles)


class UserListCreateView(APIView):
    """List users (only lower level) and create user. Hierarchy-based."""
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get(self, request):
        """List users the requester can manage (lower level only)."""
        users = _managed_users(request).select_related('created_by', 'deactivated_by').order_by('-created_at')
        serializer = UserSerializer(users, many=True)
        return Response(success_response(serializer.data, "Users retrieved successfully"))

    def post(self, request):
        """Create user. Can only assign lower-level roles."""
        serializer = UserCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                success_response(UserSerializer(user).data, "User created successfully"),
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserDetailView(APIView):
    """Retrieve, update, remove user. Can only manage lower-level users."""
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get_object(self, pk):
        user = User.objects.select_related('created_by', 'deactivated_by').filter(pk=pk).first()
        if not user:
            from rest_framework.exceptions import NotFound
            raise NotFound("User not found")
        return user

    def _check_can_manage(self, request, user):
        from rest_framework.exceptions import PermissionDenied
        if not can_manage(request.user, user):
            raise PermissionDenied("You can only manage users with lower hierarchy level.")

    def get(self, request, pk):
        """Get user by ID (only if requester can manage them)."""
        user = self.get_object(pk)
        self._check_can_manage(request, user)
        serializer = UserSerializer(user)
        return Response(success_response(serializer.data, "User retrieved successfully"))

    def put(self, request, pk):
        """Update user. Role editable only by higher-level users."""
        user = self.get_object(pk)
        self._check_can_manage(request, user)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            user.refresh_from_db()
            return Response(success_response(UserSerializer(user).data, "User updated successfully"))
        return Response(
            {"success": False, "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Remove user (soft delete: status inactive, deactivated_by set)."""
        user = self.get_object(pk)
        self._check_can_manage(request, user)
        if user == request.user:
            return Response(
                {"success": False, "message": "You cannot remove your own account", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.deactivated_by = request.user
        user.deactivated_at = timezone.now()
        user.save()
        serializer = UserSerializer(user)
        return Response(success_response(serializer.data, "User removed successfully"), status=status.HTTP_200_OK)
