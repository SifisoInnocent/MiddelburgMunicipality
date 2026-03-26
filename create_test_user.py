import os
import sys
import django

# Add project directory to Python path
sys.path.append('c:\\Users\\Admin\\Desktop\\municipal-helpdesk')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    
    print("Creating test user...")
    
    # Delete existing test user if exists
    try:
        existing_user = User.objects.get(username='testuser')
        print(f"Deleting existing test user: {existing_user.username}")
        existing_user.delete()
    except User.DoesNotExist:
        print("No existing test user found")
    
    # Create new test user
    try:
        test_user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=test_user, role='user')
        print(f"✅ Created test user: testuser")
        print("✅ Created user profile")
        
        # Create a test issue for this user
        from issues.models import Issue
        test_issue = Issue.objects.create(
            user=test_user,
            title='Test Issue for Dashboard',
            category='water',
            description='This is a test issue to verify dashboard functionality.',
            location='123 Test Street',
            reference_number='TEST-DASH-001'
        )
        print(f"✅ Created test issue: {test_issue.reference_number}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Django setup error: {e}")
    import traceback
    traceback.print_exc()
