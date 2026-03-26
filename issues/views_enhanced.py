from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
import json

from .models import Issue, IssueCategory, IssueComment, IssueVote, IssueHistory, IssueSubscription
from .forms import IssueForm, IssueCommentForm, IssueUpdateForm
from accounts.models import UserActivity, UserProfile

class IssueForm(forms.ModelForm):
    """Enhanced IssueForm with validation and widgets"""
    class Meta:
        model = Issue
        fields = ['title', 'category', 'priority', 'description', 'location', 
                 'location_accuracy', 'latitude', 'longitude', 'image', 'attachment', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Brief summary of the issue',
                'required': True
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide detailed information about the issue...',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the exact location or address',
                'required': True
            }),
            'location_accuracy': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'GPS latitude (optional)'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'GPS longitude (optional)'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'tag1, tag2, tag3 (optional)'
            }),
        }

class IssueCommentForm(forms.ModelForm):
    """Form for adding comments to issues"""
    class Meta:
        model = IssueComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment...',
                'required': True
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class IssueUpdateForm(forms.ModelForm):
    """Form for updating issue status and assignment"""
    class Meta:
        model = Issue
        fields = ['status', 'priority', 'assigned_to', 'estimated_resolution_time', 'public_visibility']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'estimated_resolution_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'public_visibility': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

@login_required
def dashboard(request):
    """Enhanced dashboard with advanced features"""
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    date_filter = request.GET.get('date', '')
    
    # Base queryset
    user_issues = Issue.objects.filter(user=request.user)
    
    # Apply filters
    if search_query:
        user_issues = user_issues.filter(
            Q(title__icontains=search_query) | 
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if status_filter:
        user_issues = user_issues.filter(status=status_filter)
    
    if priority_filter:
        user_issues = user_issues.filter(priority=priority_filter)
    
    if category_filter:
        user_issues = user_issues.filter(category_id=category_filter)
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            user_issues = user_issues.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timezone.timedelta(days=7)
            user_issues = user_issues.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timezone.timedelta(days=30)
            user_issues = user_issues.filter(created_at__date__gte=month_ago)
    
    # Order by priority and creation date
    priority_order = {'critical': 1, 'urgent': 2, 'high': 3, 'medium': 4, 'low': 5}
    user_issues = sorted(user_issues, key=lambda x: priority_order.get(x.priority, 4))
    
    # Pagination
    paginator = Paginator(user_issues, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    stats = {
        'total': user_issues.count(),
        'submitted': user_issues.filter(status='submitted').count(),
        'under_review': user_issues.filter(status='under_review').count(),
        'in_progress': user_issues.filter(status='in_progress').count(),
        'resolved': user_issues.filter(status='resolved').count(),
        'critical': user_issues.filter(priority='critical').count(),
        'urgent': user_issues.filter(priority='urgent').count(),
        'overdue': sum(1 for issue in user_issues if issue.is_overdue),
    }
    
    # Get categories for filter
    categories = IssueCategory.objects.filter(is_active=True)
    
    # Get recent activity
    recent_activity = IssueHistory.objects.filter(
        issue__user=request.user
    ).select_related('issue', 'user').order_by('-created_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'categories': categories,
        'recent_activity': recent_activity,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'date_filter': date_filter,
        'user': request.user,
    }
    
    return render(request, 'issues/dashboard.html', context)

@login_required
def report_issue(request):
    """Enhanced issue reporting with validation and tracking"""
    # Check rate limiting
    cache_key = f'issue_report_{request.user.id}'
    recent_reports = cache.get(cache_key, 0)
    max_reports = settings.HELPDESK_SETTINGS.get('MAX_ISSUES_PER_USER_PER_DAY', 10)
    
    if recent_reports >= max_reports:
        messages.error(request, f'You have reached the daily limit of {max_reports} issue reports.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                issue = form.save(commit=False)
                issue.user = request.user
                issue.save()
                
                # Track activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='issue_reported',
                    description=f'Reported issue: {issue.title}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Update user stats
                try:
                    profile = request.user.userprofile
                    profile.issues_reported += 1
                    profile.save()
                except UserProfile.DoesNotExist:
                    UserProfile.objects.create(
                        user=request.user,
                        issues_reported=1
                    )
                
                # Create history entry
                IssueHistory.objects.create(
                    issue=issue,
                    user=request.user,
                    action='issue_created',
                    description=f'Issue {issue.reference_number} created'
                )
                
                # Update rate limit cache
                cache.set(cache_key, recent_reports + 1, 86400)  # 24 hours
                
                messages.success(request, f'✅ Issue reported successfully! Reference: {issue.reference_number}')
                return redirect('track_issue', reference_number=issue.reference_number)
    else:
        form = IssueForm()
    
    # Get active categories
    categories = IssueCategory.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'categories': categories,
        'remaining_reports': max_reports - recent_reports,
    }
    
    return render(request, 'issues/report_issue.html', context)

@login_required
def track_issue(request, reference_number):
    """Enhanced issue tracking with comments and history"""
    issue = get_object_or_404(Issue, reference_number=reference_number, user=request.user)
    
    # Increment view count
    issue.view_count += 1
    issue.save(update_fields=['view_count'])
    
    # Get status progression
    status_steps = ['submitted', 'under_review', 'in_progress', 'resolved']
    current_index = status_steps.index(issue.status) if issue.status in status_steps else 0
    
    # Handle comment submission
    if request.method == 'POST':
        comment_form = IssueCommentForm(request.POST)
        if comment_form.is_valid():
            with transaction.atomic():
                comment = comment_form.save(commit=False)
                comment.issue = issue
                comment.user = request.user
                comment.save()
                
                # Track activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='comment_added',
                    description=f'Commented on issue: {issue.reference_number}'
                )
                
                # Create history entry
                IssueHistory.objects.create(
                    issue=issue,
                    user=request.user,
                    action='comment_added',
                    description=f'Comment added: {comment.content[:50]}...'
                )
                
                messages.success(request, 'Comment added successfully!')
                return redirect('track_issue', reference_number=reference_number)
    else:
        comment_form = IssueCommentForm()
    
    # Get comments (exclude internal for non-staff)
    comments = issue.comments.filter(is_internal=False).select_related('user')
    
    # Get history
    history = issue.history.select_related('user').order_by('-created_at')
    
    # Check if user is subscribed
    is_subscribed = IssueSubscription.objects.filter(issue=issue, user=request.user).exists()
    
    context = {
        'issue': issue,
        'status_steps': status_steps,
        'current_index': current_index,
        'comments': comments,
        'history': history,
        'comment_form': comment_form,
        'is_subscribed': is_subscribed,
    }
    
    return render(request, 'issues/track_issue.html', context)

@login_required
@require_POST
def vote_issue(request, reference_number):
    """Handle voting on issues"""
    issue = get_object_or_404(Issue, reference_number=reference_number)
    
    if not issue.can_vote(request.user):
        return JsonResponse({'error': 'You cannot vote on this issue'}, status=400)
    
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    with transaction.atomic():
        # Create or update vote
        vote, created = IssueVote.objects.get_or_create(
            issue=issue,
            user=request.user,
            defaults={'vote_type': vote_type}
        )
        
        if not created:
            # Update existing vote
            vote.vote_type = vote_type
            vote.save()
        
        # Update issue vote counts
        upvotes = IssueVote.objects.filter(issue=issue, vote_type='up').count()
        downvotes = IssueVote.objects.filter(issue=issue, vote_type='down').count()
        
        issue.upvotes = upvotes
        issue.downvotes = downvotes
        issue.save(update_fields=['upvotes', 'downvotes'])
        
        # Track activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='issue_voted',
            description=f'{vote_type}voted issue: {issue.reference_number}'
        )
    
    return JsonResponse({
        'success': True,
        'upvotes': upvotes,
        'downvotes': downvotes,
        'user_vote': vote_type
    })

@login_required
@require_POST
def subscribe_issue(request, reference_number):
    """Handle issue subscriptions"""
    issue = get_object_or_404(Issue, reference_number=reference_number)
    
    with transaction.atomic():
        subscription, created = IssueSubscription.objects.get_or_create(
            issue=issue,
            user=request.user
        )
        
        if not created:
            # Unsubscribe
            subscription.delete()
            action = 'unsubscribed'
        else:
            action = 'subscribed'
        
        # Track activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='issue_subscribed',
            description=f'{action} to issue: {issue.reference_number}'
        )
    
    return JsonResponse({
        'success': True,
        'subscribed': created,
        'action': action
    })

@login_required
def issue_analytics(request):
    """Analytics dashboard for user issues"""
    user_issues = Issue.objects.filter(user=request.user)
    
    # Basic statistics
    total_issues = user_issues.count()
    resolved_issues = user_issues.filter(status='resolved').count()
    
    # Resolution time analytics
    resolution_times = [
        (issue.resolved_at - issue.created_at).days 
        for issue in user_issues.filter(status='resolved', resolved_at__isnull=False)
    ]
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    # Category breakdown
    category_stats = user_issues.values('category__display_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status progression over time
    status_timeline = user_issues.extra(
        select={'month': 'strftime("%%Y-%%m", created_at)'}
    ).values('month', 'status').annotate(count=Count('id')).order_by('month')
    
    # Priority distribution
    priority_stats = user_issues.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_issues': total_issues,
        'resolved_issues': resolved_issues,
        'resolution_rate': (resolved_issues / total_issues * 100) if total_issues > 0 else 0,
        'avg_resolution_time': round(avg_resolution_time, 1),
        'category_stats': category_stats,
        'status_timeline': status_timeline,
        'priority_stats': priority_stats,
    }
    
    return render(request, 'issues/analytics.html', context)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
