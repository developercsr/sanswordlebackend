"""
Favorites URL configuration.
"""
from django.urls import path
from .views import FavoritesGetView, FavoritesAddView, FavoritesRemoveView

urlpatterns = [
    path('', FavoritesGetView.as_view(), name='favorites-get'),
    path('add/', FavoritesAddView.as_view(), name='favorites-add'),
    path('remove/', FavoritesRemoveView.as_view(), name='favorites-remove'),
]
