"""
Global exception handling for the API.
Returns structured JSON responses for all error types.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns structured responses:
    {
        "success": false,
        "message": "error message",
        "data": null
    }
    """
    if isinstance(exc, Http404):
        exc = exc
    elif isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": str(exc) or "You do not have permission to perform this action.",
                "data": None
            },
            status=status.HTTP_403_FORBIDDEN
        )
    elif isinstance(exc, ValidationError):
        message = exc
        if hasattr(exc, 'message_dict'):
            message = "; ".join(
                f"{k}: {v}" if isinstance(v, str) else f"{k}: {', '.join(v)}"
                for k, v in exc.message_dict.items()
            )
        elif hasattr(exc, 'messages'):
            message = "; ".join(str(m) for m in exc.messages)
        return Response(
            {
                "success": False,
                "message": str(message),
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "message": response.data.get('detail', str(exc)) if isinstance(response.data, dict) else str(exc),
            "data": None
        }
        if isinstance(response.data, dict) and 'detail' not in response.data:
            custom_data["message"] = str(response.data)
        response.data = custom_data
        return response

    return Response(
        {
            "success": False,
            "message": str(exc) or "An unexpected error occurred.",
            "data": None
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
