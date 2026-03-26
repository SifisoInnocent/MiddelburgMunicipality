from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def custom_login(request):
    """Custom login view with role-based redirection"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Check user role and redirect accordingly
            try:
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login_premium.html', {'form': form})

def register(request):
    """User registration page"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'user')
        
        if form.is_valid():
            user = form.save()
            # Create user profile with role
            UserProfile.objects.create(user=user, role=role)
            login(request, user)  # Auto-login after registration
            messages.success(request, 'Account created successfully!')
            
            # Redirect based on role
            if role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register_premium.html', {'form': form})

def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')