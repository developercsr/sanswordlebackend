"""
URL configuration for Sanskrit Wordle backend.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def api_root(request):
    """Root path - returns API info and available endpoints."""
    return JsonResponse({
        "success": True,
        "message": "SansWordle API",
        "data": {
            "version": "1.0",
            "endpoints": {
                "auth": "/api/auth/login/ | /api/auth/refresh/",
                "users": "/api/users/ | /api/users/<id>/",
                "profile": "/api/profile/",
                "words": "/api/words/ | /api/words/upload/ | /api/words/<id>/ | /api/words/<id>/verify/ | /api/words/excel-template/download/ | /api/words/excel-upload/",
                "admin": "/admin/"
            }
        }
    })


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls.auth')),
    path('api/users/', include('apps.users.urls.users')),
    path('api/profile/', include('apps.users.urls.profile')),
    path('api/words/', include('apps.words.urls')),
    path('api/checkwords/', include('apps.words.urls_checkwords')),
    path('api/favorites/', include('apps.favorites.urls')),
]
