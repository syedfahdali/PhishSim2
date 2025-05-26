from django.shortcuts import redirect
from django.urls import reverse
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to unauthenticated users
        if not request.user.is_authenticated:
            resolver_match = resolve(request.path_info)
            if resolver_match.url_name not in EXEMPT_URLS:
                return redirect('login')
        return self.get_response(request)

EXEMPT_URLS = [
    'login',
    'register',
    'activate',
    'resend_activation',
    'admin:login',
    'static',
    '',  # root/index
]