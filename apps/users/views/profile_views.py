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
