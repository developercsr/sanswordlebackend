"""
Global exception middleware to catch unhandled exceptions
outside of DRF views and return structured JSON responses.
"""
import json
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class GlobalExceptionMiddleware(MiddlewareMixin):
    """
    Catches unhandled exceptions and returns structured JSON response.
    """

    def process_exception(self, request, exception):
        """Handle exception and return structured response."""
        if request.path.startswith('/api/'):
            return JsonResponse(
                {
                    "success": False,
                    "message": str(exception) or "An unexpected error occurred.",
                    "data": None
                },
                status=500
            )
        return None
