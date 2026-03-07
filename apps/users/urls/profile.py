"""
Profile URL configuration.
"""
from django.urls import path
from apps.users.views.profile_views import ProfileView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
]
