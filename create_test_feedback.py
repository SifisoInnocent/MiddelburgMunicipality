#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')
django.setup()

from issues.models import Issue, Feedback
from django.contrib.auth.models import User

def create_test_feedback():
    print("Creating test feedback...")
    
    # Get existing issues and admin user
    issues = Issue.objects.all()
    admin_users = User.objects.filter(is_superuser=True)
    
    if not issues:
        print("No issues found. Please create some issues first.")
        return
    
    if not admin_users:
        print("No admin users found. Creating admin user...")
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("Created admin user: admin/admin123")
        admin_users = [admin]
    
    admin = admin_users[0]
    
    # Add feedback to first few issues
    for i, issue in enumerate(issues[:3]):
        feedback_messages = [
            "We have received your report and our team is investigating the issue. Thank you for bringing this to our attention.",
            "Our maintenance team has been dispatched to address this issue. We expect to resolve it within 2-3 business days.",
            "This issue has been successfully resolved. Please let us know if you experience any further problems."
        ]
        
        if i < len(feedback_messages):
            feedback = Feedback.objects.create(
                issue=issue,
                admin=admin,
                message=feedback_messages[i]
            )
            print(f"Added feedback to issue {issue.reference_number}: {feedback.message[:50]}...")

if __name__ == '__main__':
    create_test_feedback()
    print("\nFeedback creation complete!")
    print(f"Total feedback entries: {Feedback.objects.count()}")
