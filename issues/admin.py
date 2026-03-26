from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Issue

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'title', 'category', 'status', 'user', 'created_at', 'updated_at', 'action_buttons')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'location', 'reference_number', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    list_per_page = 20
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'category', 'status')
        }),
        ('Details', {
            'fields': ('description', 'location', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj)
        
        # Send notification on status change
        if obj.pk:
            original = Issue.objects.get(pk=obj.pk)
            if original.status != obj.status:
                self.send_status_update_notification(obj)
    
    def send_status_update_notification(self, obj):
        """Send notification to user about status change"""
        subject = f'Issue Status Updated: {obj.title}'
        message = f'''
        Dear {obj.user.username},
        
        Your issue "{obj.title}" (Reference: {obj.reference_number}) 
        has been updated to: {obj.get_status_display()}
        
        New Status: {obj.get_status_display()}
        Location: {obj.location}
        
        You can track the progress here: {reverse("track_issue", args=[obj.reference_number])}
        
        Thank you for your patience!
        
        Municipal Helpdesk Team
        '''
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [obj.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send status update email: {e}")
    
    def action_buttons(self, obj):
        """Custom action buttons for list view"""
        if obj.status == 'submitted':
            return format_html(
                '<a class="button" href="{}?action=assign&issue_id={}">Assign</a>',
                reverse('admin:issues_issue_change', args=[obj.pk]),
                obj.pk
            )
        elif obj.status == 'in_progress':
            return format_html(
                '<a class="button" href="{}?action=resolve&issue_id={}">Resolve</a>',
                reverse('admin:issues_issue_change', args=[obj.pk]),
                obj.pk
            )
        return ''
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist view to add custom actions"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Issue Management - Real-time Updates'
        
        # Handle custom actions
        if 'action' in request.GET:
            action = request.GET.get('action')
            issue_id = request.GET.get('issue_id')
            
            if action == 'assign' and issue_id:
                try:
                    issue = Issue.objects.get(pk=issue_id)
                    issue.status = 'in_progress'
                    issue.save()
                    self.message_user(request, f'Issue {issue.reference_number} assigned and marked as in progress.')
                except Issue.DoesNotExist:
                    self.message_user(request, 'Issue not found.')
            
            elif action == 'resolve' and issue_id:
                try:
                    issue = Issue.objects.get(pk=issue_id)
                    issue.status = 'resolved'
                    issue.save()
                    self.message_user(request, f'Issue {issue.reference_number} marked as resolved.')
                except Issue.DoesNotExist:
                    self.message_user(request, 'Issue not found.')
        
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('admin/custom_admin.css',)
        }
        js = ('admin/custom_admin.js',)
