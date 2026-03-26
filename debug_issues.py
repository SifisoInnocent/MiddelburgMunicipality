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
    from issues.models import Issue
    
    print("Checking database for issues...")
    
    # Check all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    # Check all user profiles
    profiles = UserProfile.objects.all()
    print(f"Total profiles: {profiles.count()}")
    
    # Check all issues
    issues = Issue.objects.all()
    print(f"Total issues in database: {issues.count()}")
    
    # Show issues by user
    for user in users:
        user_issues = Issue.objects.filter(user=user)
        print(f"User '{user.username}' has {user_issues.count()} issues:")
        for issue in user_issues:
            print(f"  - {issue.reference_number}: {issue.title} ({issue.status})")
    
    # Check specific test user
    try:
        test_user = User.objects.get(username='testuser')
        test_user_issues = Issue.objects.filter(user=test_user)
        print(f"\nTest user 'testuser' has {test_user_issues.count()} issues:")
        for issue in test_user_issues:
            print(f"  - {issue.reference_number}: {issue.title} ({issue.status})")
    except User.DoesNotExist:
        print("Test user not found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
