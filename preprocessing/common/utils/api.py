"""
Utilities for API responses.
"""
from django.http import JsonResponse


class APIResponse:
    """Helper class for consistent API responses."""

    @staticmethod
    def success(data=None, message=None, status=200):
        """Return a success response."""
        response_data = {'success': True}

        if message:
            response_data['message'] = message

        if data:
            response_data['data'] = data

        return JsonResponse(response_data, status=status)

    @staticmethod
    def error(message, status=400, errors=None):
        """Return an error response."""
        response_data = {
            'success': False,
            'message': message
        }

        if errors:
            response_data['errors'] = errors

        return JsonResponse(response_data, status=status)

    @staticmethod
    def created(data=None, message=None):
        """Return a 201 Created response."""
        return APIResponse.success(data=data, message=message, status=201)

    @staticmethod
    def not_found(message="Resource not found"):
        """Return a 404 Not Found response."""
        return APIResponse.error(message=message, status=404)

    @staticmethod
    def bad_request(message, errors=None):
        """Return a 400 Bad Request response."""
        return APIResponse.error(message=message, status=400, errors=errors)

    @staticmethod
    def unauthorized(message="Authentication required"):
        """Return a 401 Unauthorized response."""
        return APIResponse.error(message=message, status=401)

    @staticmethod
    def forbidden(message="Permission denied"):
        """Return a 403 Forbidden response."""
        return APIResponse.error(message=message, status=403)
