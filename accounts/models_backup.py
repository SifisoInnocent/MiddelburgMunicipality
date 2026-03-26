from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    """Enhanced user profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=False, help_text="Make your profile public")
    
    # Location information
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Social links
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True, help_text="Twitter username without @")
    linkedin = models.CharField(max_length=50, blank=True, help_text="LinkedIn username")
    
    # Statistics
    issues_reported = models.PositiveIntegerField(default=0)
    issues_resolved = models.PositiveIntegerField(default=0)
    reputation_points = models.IntegerField(default=0)
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text="Verified citizen")
    verification_document = models.FileField(
        upload_to='verification/',
        blank=True,
        null=True,
        help_text="Upload ID for verification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.phone_number, self.address, self.bio, self.avatar,
            self.date_of_birth, self.city, self.state, self.country,
            self.postal_code, self.website
        ]
        filled_fields = sum(1 for field in fields if field)
        return round((filled_fields / len(fields)) * 100, 0)

class UserActivity(models.Model):
    """Track user activities for engagement metrics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)  # 'login', 'issue_reported', 'comment_added', etc.
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class UserBadge(models.Model):
    """Achievement badges for users"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    points_required = models.PositiveIntegerField(default=0)
    badge_type = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], default='bronze')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['points_required', 'name']
    
    def __str__(self):
        return self.name

class UserBadgeEarned(models.Model):
    """Track badges earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(UserBadge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"

class UserPreference(models.Model):
    """User-specific preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Theme preferences
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ], default='light')
    
    # Notification preferences
    email_issue_updates = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_resolutions = models.BooleanField(default=True)
    sms_issue_updates = models.BooleanField(default=False)
    
    # Privacy preferences
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    allow_messages = models.BooleanField(default=True)
    
    # Language and timezone
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Dashboard preferences
    dashboard_layout = models.CharField(max_length=20, choices=[
        ('grid', 'Grid'),
        ('list', 'List'),
        ('cards', 'Cards'),
    ], default='cards')
    
    items_per_page = models.PositiveIntegerField(default=10, choices=[
        (5, '5'),
        (10, '10'),
        (20, '20'),
        (50, '50'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"
