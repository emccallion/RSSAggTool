"""
Decorators for common patterns like AJAX response handling.
"""
from functools import wraps
from django.http import JsonResponse


def ajax_response(func):
    """
    Decorator that wraps view functions to automatically handle JSON responses.

    The decorated function should return a dictionary on success, which will be
    wrapped in a success response. Exceptions are automatically caught and
    returned as error responses.

    Example:
        @ajax_response
        def my_view(request):
            data = do_something()
            return {'message': 'Success!', 'data': data}
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            result = func(request, *args, **kwargs)

            # If function returns a JsonResponse, return it directly
            if isinstance(result, JsonResponse):
                return result

            # Otherwise, wrap the result in a success response
            if isinstance(result, dict):
                response_data = {'success': True}
                response_data.update(result)
                return JsonResponse(response_data)

            # If no dict returned, just indicate success
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    return wrapper


def ajax_login_required(func):
    """
    Decorator that checks if user is authenticated for AJAX requests.
    Returns JSON error response if not authenticated.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)
        return func(request, *args, **kwargs)
    return wrapper
