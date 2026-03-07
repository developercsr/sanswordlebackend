"""
Utility functions for the Sanskrit Wordle backend.
"""


def success_response(data=None, message="Success"):
    """
    Return a standardized success response structure.
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }
