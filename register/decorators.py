from functools import wraps
from django.http import HttpResponseForbidden

def admin_required(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return function(request, *args, **kwargs)
    return wrapper
