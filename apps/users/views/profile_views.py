"""
Profile views - get and update own profile.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import ProfileSerializer
from core.utils import success_response


class ProfileView(APIView):
    """Get and update own profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user's profile."""
        serializer = ProfileSerializer(request.user)
        return Response(success_response(serializer.data, "Profile retrieved successfully"))

    def put(self, request):
        """Update current user's profile."""
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(success_response(serializer.data, "Profile updated successfully"))
        return Response(
            {"success": False, "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfilePhotoUploadView(APIView):
    """
    POST /api/profile/photo
    Upload and update current user's profile photo.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get("profile_photo")
        if not file_obj:
            return Response(
                {"status": "error", "message": "profile_photo file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file_obj.content_type.startswith("image/"):
            return Response(
                {"status": "error", "message": "Only image files are allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.profile_photo = file_obj
        user.save(update_fields=["profile_photo"])
        photo_url = user.profile_photo.url if user.profile_photo else None
        return Response(
            {"status": "success", "profile_photo_url": photo_url},
            status=status.HTTP_200_OK,
        )
