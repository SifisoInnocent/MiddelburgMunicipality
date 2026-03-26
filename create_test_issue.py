#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    from issues.models import Issue
    
    print("Creating test issue...")
    
    # Create test user if doesn't exist
    try:
        test_user = User.objects.get(username='user1')
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='user123'
        )
        UserProfile.objects.create(user=test_user, role='user')
        print("✅ Created test user: user1")
    
    # Create test issue
    issue = Issue.objects.create(
        user=test_user,
        title='Test Water Leak',
        category='water',
        description='This is a test water leak issue for tracking purposes.',
        location='123 Main Street',
        reference_number='TEST-001'
    )
    
    print(f"✅ Created test issue: {issue.reference_number}")
    print("You can now track this issue at: /track/TEST-001/")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
