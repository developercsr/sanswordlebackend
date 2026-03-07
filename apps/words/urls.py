"""
Words URL configuration.
"""
from django.urls import path
from .views import WordListCreateView, WordDetailView, WordVerifyView

urlpatterns = [
    path('', WordListCreateView.as_view(), name='word-list-create'),
    path('<int:pk>/', WordDetailView.as_view(), name='word-detail'),
    path('<int:pk>/verify/', WordVerifyView.as_view(), name='word-verify'),
]
