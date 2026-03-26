from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
import uuid

class IssueCategory(models.Model):
    """Enhanced category model with more details"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#3498db", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Issue Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.display_name

class Issue(models.Model):
    """Enhanced Issue model with advanced features"""
    
    # Status options
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    # Priority options
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]
    
    # Location accuracy
    LOCATION_ACCURACY_CHOICES = [
        ('exact', 'Exact Address'),
        ('approximate', 'Approximate'),
        ('area', 'Area Only'),
    ]
    
    # Category options
    CATEGORY_CHOICES = [
        ('water', '💧 Water Leak'),
        ('pothole', '🕳️ Pothole'),
        ('electricity', '⚡ Electricity Fault'),
        ('waste', '🗑️ Waste Collection'),
        ('other', '📌 Other'),
    ]
    
    # Core fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(help_text="Detailed description of the issue")
    
    # Location information
    location = models.CharField(max_length=500)
    location_accuracy = models.CharField(max_length=20, choices=LOCATION_ACCURACY_CHOICES, default='exact')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Priority and status
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    # Media attachments
    image = models.ImageField(
        upload_to='issues/images/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=settings.HELPDESK_SETTINGS.get('ALLOWED_FILE_TYPES', ['jpg', 'jpeg', 'png', 'gif']))]
    )
    
    # Additional files
    attachment = models.FileField(
        upload_to='issues/attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt'])]
    )
    
    # Tracking and timestamps
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment and workflow
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_issues',
        help_text="Staff member assigned to this issue"
    )
    estimated_resolution_time = models.DateTimeField(null=True, blank=True, help_text="Estimated time for resolution")
    
    # Additional metadata
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    public_visibility = models.BooleanField(default=True, help_text="Make this issue visible to public")
    anonymous_reporting = models.BooleanField(default=False, help_text="Report anonymously")
    
    # Voting and engagement
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['reference_number']),
        ]
    
    def save(self, *args, **kwargs):
        # Generate unique reference number
        if not self.reference_number:
            self.reference_number = f"SR-{uuid.uuid4().hex[:8].upper()}"
        
        # Auto-set timestamps based on status changes
        old_status = None
        if self.pk:
            try:
                old_instance = Issue.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Issue.DoesNotExist:
                pass
        
        # Set resolved timestamp
        if self.status == 'resolved' and (old_status != 'resolved' or not self.resolved_at):
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None
        
        # Set closed timestamp
        if self.status in ['closed', 'rejected'] and (old_status not in ['closed', 'rejected'] or not self.closed_at):
            self.closed_at = timezone.now()
        elif self.status not in ['closed', 'rejected']:
            self.closed_at = None
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference_number} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if issue is overdue based on estimated resolution time"""
        if self.estimated_resolution_time and self.status not in ['resolved', 'closed', 'rejected']:
            return timezone.now() > self.estimated_resolution_time
        return False
    
    @property
    def days_open(self):
        """Calculate how many days the issue has been open"""
        return (timezone.now() - self.created_at).days
    
    @property
    def can_vote(self, user):
        """Check if user can vote on this issue"""
        if not user.is_authenticated:
            return False
        if self.user == user:
            return False
        return not IssueVote.objects.filter(issue=self, user=user).exists()
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

class IssueComment(models.Model):
    """Comments on issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal comment (only visible to staff)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.issue.reference_number}"

class IssueVote(models.Model):
    """Voting system for issues"""
    VOTE_CHOICES = [('up', 'Upvote'), ('down', 'Downvote')]
    
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['issue', 'user']
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type}voted {self.issue.reference_number}"

class IssueHistory(models.Model):
    """Track all changes to issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # e.g., 'status_changed', 'assigned', 'comment_added'
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} on {self.issue.reference_number} by {self.user.username}"

class IssueSubscription(models.Model):
    """Users can subscribe to issues for updates"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='subscribers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['issue', 'user']
    
    def __str__(self):
        return f"{self.user.username} subscribed to {self.issue.reference_number}"