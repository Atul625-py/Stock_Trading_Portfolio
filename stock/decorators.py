from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='Users').exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='Admins').exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
