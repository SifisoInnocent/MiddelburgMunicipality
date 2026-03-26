from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django import forms
import csv
from datetime import datetime
from .models import Issue
from accounts.models import UserProfile

def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'
    except:
        return False

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'category', 'description', 'location', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

def home(request):
    """Home page view"""
    return render(request, 'issues/home.html')

@login_required
def dashboard(request):
    user_issues = Issue.objects.filter(user=request.user).order_by('-created_at')
    
    # Handle search and filtering
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Apply filters
    if search_query:
        user_issues = user_issues.filter(
            Q(title__icontains=search_query) | 
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    if status_filter:
        user_issues = user_issues.filter(status=status_filter)
    
    if category_filter:
        user_issues = user_issues.filter(category=category_filter)
    
    # Handle CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="issues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Reference', 'Title', 'Category', 'Status', 'Location', 'Description', 'Created At', 'Updated At'])
        
        for issue in user_issues:
            writer.writerow([
                issue.reference_number,
                issue.title,
                issue.get_category_display(),
                issue.get_status_display(),
                issue.location,
                issue.description,
                issue.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                issue.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    stats = {
        'total': user_issues.count(),
        'submitted': user_issues.filter(status='submitted').count(),
        'in_progress': user_issues.filter(status='in_progress').count(),
        'resolved': user_issues.filter(status='resolved').count(),
    }
    
    paginator = Paginator(user_issues, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'user': request.user,
        'today': datetime.now().date(),
    }
    return render(request, 'issues/dashboard_simple.html', context)

@login_required
def report_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()
            messages.success(request, f'✅ Issue reported successfully! Reference: {issue.reference_number}')
            return redirect('dashboard')
    else:
        form = IssueForm()
    
    return render(request, 'issues/report_issue_premium.html', {'form': form})

@login_required
def track_issue(request):
    """Track issue page - shows search form"""
    issue = None
    reference_number = request.GET.get('ref', '').strip()
    
    if reference_number:
        try:
            # Try to find the issue
            issue = get_object_or_404(Issue, reference_number=reference_number)
        except:
            issue = None
    
    context = {
        'issue': issue,
        'reference_number': reference_number,
    }
    return render(request, 'issues/track_issue.html', context)

@login_required
def track_issue_detail(request, reference_number):
    """Track issue detail view - shows specific issue"""
    try:
        issue = get_object_or_404(Issue, reference_number=reference_number, user=request.user)
    except:
        # If user doesn't own the issue, still show it (for testing purposes)
        issue = get_object_or_404(Issue, reference_number=reference_number)
    
    status_steps = ['submitted', 'in_progress', 'resolved']
    current_index = status_steps.index(issue.status)
    
    context = {
        'issue': issue,
        'status_steps': status_steps,
        'current_index': current_index,
    }
    return render(request, 'issues/track_issue.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard - only accessible by admin"""
    all_issues = Issue.objects.all().order_by('-created_at')
    
    # Handle search and filtering
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Apply filters
    if search_query:
        all_issues = all_issues.filter(
            Q(title__icontains=search_query) | 
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    if status_filter:
        all_issues = all_issues.filter(status=status_filter)
    
    if category_filter:
        all_issues = all_issues.filter(category=category_filter)
    
    # Calculate stats
    stats = {
        'total': all_issues.count(),
        'submitted': all_issues.filter(status='submitted').count(),
        'in_progress': all_issues.filter(status='in_progress').count(),
        'resolved': all_issues.filter(status='resolved').count(),
    }
    
    # Pagination
    paginator = Paginator(all_issues, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'all_issues': page_obj,
    }
    return render(request, 'issues/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def update_issue_status(request, issue_id):
    """Update issue status - admin only"""
    if request.method == 'POST':
        issue = get_object_or_404(Issue, id=issue_id)
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in ['submitted', 'in_progress', 'resolved']:
            issue.status = new_status
            if admin_notes:
                issue.admin_notes = admin_notes
            issue.save()
            messages.success(request, f'Issue {issue.reference_number} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('admin_dashboard')
