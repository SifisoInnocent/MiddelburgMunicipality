from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Issue

@receiver(post_save, sender=Issue)
def issue_status_update(sender, instance, created, **kwargs):
    """Send real-time notifications when issue status changes"""
    if not created:  # Only for updates, not new issues
        # Send email to issue reporter
        subject = f'Issue Update: {instance.title}'
        message = f'''
        Dear {instance.user.username},

        Your reported issue "{instance.title}" (Reference: {instance.reference_number}) 
        has been updated to: {instance.get_status_display()}

        Current Status: {instance.get_status_display()}
        Location: {instance.location}
        Description: {instance.description}

        You can track the progress here: http://127.0.0.1:8000/track/{instance.reference_number}/

        Thank you for helping improve our community!
        
        Municipal Helpdesk Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    # Notify admin users about new issues
    if created:
        subject = f'New Issue Reported: {instance.title}'
        message = f'''
        A new issue has been reported:
        
        Title: {instance.title}
        Reference: {instance.reference_number}
        Category: {instance.get_category_display()}
        Status: {instance.get_status_display()}
        Location: {instance.location}
        Reported by: {instance.user.username} ({instance.user.email})
        Description: {instance.description}
        
        Please review and take appropriate action.
        
        Admin Panel: http://127.0.0.1:8000/admin/
        '''
        
        # Send to all admin users
        admin_users = User.objects.filter(is_superuser=True)
        admin_emails = [admin.email for admin in admin_users]
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
