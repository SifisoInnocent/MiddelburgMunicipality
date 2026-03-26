from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to login, register, and static files
        allowed_paths = [
            reverse('login'),
            reverse('register'),
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Get current path
            current_path = request.path
            
            # Check if current path is in allowed paths
            for allowed_path in allowed_paths:
                if current_path.startswith(allowed_path):
                    return self.get_response(request)
            
            # If not authenticated and not on allowed path, redirect to login
            return redirect(reverse('login'))
        
        # If authenticated, continue normally
        return self.get_response(request)
