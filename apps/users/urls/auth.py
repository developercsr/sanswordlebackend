"""
Auth URL configuration.
"""
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views.auth_views import CustomTokenObtainPairView


class AllowAnyTokenRefreshView(TokenRefreshView):
    """Token refresh - allow unauthenticated (uses refresh token in body)."""
    permission_classes = [AllowAny]


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', AllowAnyTokenRefreshView.as_view(), name='token_refresh'),
]
