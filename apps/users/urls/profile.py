"""
Profile URL configuration.
"""
from django.urls import path
from apps.users.views.profile_views import ProfileView, ProfilePhotoUploadView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('photo', ProfilePhotoUploadView.as_view(), name='profile-photo'),
]
