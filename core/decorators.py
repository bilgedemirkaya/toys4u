from functools import wraps
from django.http import HttpResponseForbidden

def require_role(role_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Login required.")
            if not request.user.userrole_set.filter(role__role_name=role_name).exists():
                return HttpResponseForbidden(f"You need the '{role_name}' role.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_staff_type(staff_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                if request.user.staff.staff_type != staff_type:
                    return HttpResponseForbidden(f"You must be a '{staff_type}'.")
            except AttributeError:
                return HttpResponseForbidden("You are not registered as staff.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
