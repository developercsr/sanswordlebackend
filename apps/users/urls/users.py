"""
Users URL configuration.
"""
from django.urls import path
from apps.users.views.user_views import (
    UserListCreateView,
    UserDetailView,
    SimpleUserCreateView,
    MyUsersView,
    UpdateUserRoleView,
    WordActivityView,
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('create', SimpleUserCreateView.as_view(), name='user-simple-create'),
    path('my-users', MyUsersView.as_view(), name='user-my-users'),
    path('update-role', UpdateUserRoleView.as_view(), name='user-update-role'),
    path('word-activity', WordActivityView.as_view(), name='user-word-activity'),
    path('activity', WordActivityView.as_view(), name='user-activity'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
