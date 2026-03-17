"""
User CRUD views - hierarchy-based.
Higher level users can manage (list/create/update/remove) lower level users.
Remove = soft delete (status inactive, deactivated_by set).
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from apps.users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from apps.users.permissions import CanManageUsers
from apps.users.hierarchy import can_manage, get_role_level, assignable_roles, ROLE_LEVEL
from apps.words.models import Word
from apps.words.serializers import _parse_list_string
from core.utils import success_response
from apps.words.models import Word
from apps.words.serializers import _parse_list_string

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


class SimpleUserCreateView(APIView):
    """
    POST /api/users/create
    Lightweight create endpoint used by AddStaff page.
    Expects: username (email), password, role.
    """
    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request):
        data = request.data.copy()
        # Map 'username' from frontend to email/full_name for our model
        username = data.get('username') or ''
        if username:
          data.setdefault('email', username)
          data.setdefault('full_name', username)
        serializer = UserCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "User created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": "error", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MyUsersView(APIView):
    """
    GET /api/users/my-users
    Returns users created_by = current user.
    """
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get(self, request):
        users = User.objects.filter(created_by=request.user).order_by('-created_at')
        data = [
            {
                "id": u.id,
                "username": u.email,
                "role": u.role,
                "created_time": u.created_at,
            }
            for u in users
        ]
        return Response({"users": data})


class UpdateUserRoleView(APIView):
    """
    POST /api/users/update-role
    Allows creator to change role of a user they created, respecting hierarchy.
    """
    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request):
        user_id = request.data.get("user_id")
        new_role = request.data.get("role")
        if not user_id or not new_role:
            return Response(
                {"status": "error", "message": "user_id and role are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(pk=user_id, created_by=request.user).first()
        if not user:
            return Response(
                {"status": "error", "message": "User not found or not created by you"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Enforce hierarchy: actor must be able to assign this role
        if new_role == "admin" or not assignable_roles(request.user) or new_role not in assignable_roles(
            request.user
        ):
            return Response(
                {"status": "error", "message": "You cannot assign this role"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user.role = new_role
        user.save(update_fields=["role"])
        return Response({"status": "success", "message": "Role updated successfully"})


class WordActivityView(APIView):
    """
    GET /api/users/activity or /api/users/word-activity
    Query params:
      - activity_type: "uploaded", "checked", or "users_added"
      - username: partial or full email to match
    Only accessible by admin and word_manager.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activity_type = request.query_params.get("activity_type")
        username = request.query_params.get("username")

        if activity_type not in ("uploaded", "checked", "users_added") or not username:
            return Response(
                {
                    "detail": "Query parameters 'activity_type' (uploaded|checked|users_added) and 'username' are required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = getattr(request.user, "role", None)
        if role not in ("admin", "word_manager"):
            msg = (
                "Permission denied for this activity."
                if activity_type == "users_added"
                else "You do not have permission to view this feature"
            )
            return Response({"detail": msg}, status=status.HTTP_403_FORBIDDEN)

        username = username.strip()
        if activity_type == "users_added":
            users_qs = User.objects.filter(created_by__email__icontains=username).order_by(
                "-created_at"
            )
            users_data = [
                {
                    "username": u.email,
                    "role": u.role,
                    "created_time": u.created_at.date().isoformat() if u.created_at else None,
                }
                for u in users_qs
            ]
            return Response({"users": users_data})

        qs = Word.objects.all().select_related("uploaded_by", "approved_by")

        if activity_type == "uploaded":
            qs = qs.filter(uploaded_by__email__icontains=username)
        else:
            qs = qs.filter(
                Q(approved_by__email__icontains=username)
                | Q(checked_by__email__icontains=username)
            ).distinct()

        words_data = []
        for w in qs:
            class_list = _parse_list_string(w.class_name)
            chapter_list = _parse_list_string(w.chapter)
            class_val = class_list[0] if class_list else ""
            chapter_val = chapter_list[0] if chapter_list else ""

            if w.is_approved:
                status_label = "approved"
            elif w.is_rejected:
                status_label = "rejected"
            else:
                status_label = "pending"

            words_data.append(
                {
                    "word": w.word,
                    "meaning": w.meaning,
                    "class_name": class_val,
                    "chapter": chapter_val,
                    "status": status_label,
                    "date": w.created_at.date().isoformat() if w.created_at else None,
                }
            )

        return Response({"words": words_data})
