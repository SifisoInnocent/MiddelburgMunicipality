from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Issue
from django.core.paginator import Paginator

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'category', 'description', 'location', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

@login_required
def dashboard(request):
    user_issues = Issue.objects.filter(user=request.user).order_by('-created_at')
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
    }
    return render(request, 'issues/dashboard.html', context)

@login_required
def report_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()
            messages.success(request, f'Issue reported! Reference: {issue.reference_number}')
            return redirect('dashboard')
    else:
        form = IssueForm()
    
    return render(request, 'issues/report_issue.html', {'form': form})

@login_required
def track_issue(request, reference_number):
    issue = get_object_or_404(Issue, reference_number=reference_number, user=request.user)
    status_steps = ['submitted', 'in_progress', 'resolved']
    current_index = status_steps.index(issue.status)
    
    context = {
        'issue': issue,
        'status_steps': status_steps,
        'current_index': current_index,
    }
    return render(request, 'issues/track_issue.html', context)