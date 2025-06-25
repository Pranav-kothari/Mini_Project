from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def seller_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'seller':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied: Seller only")
    return _wrapped_view

def buyer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'buyer':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied: Buyer only")
    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied: Admin only")
    return _wrapped_view
