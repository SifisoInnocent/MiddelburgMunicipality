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
    
    print("Testing new user registration...")
    
    # Create test user
    try:
        existing_user = User.objects.get(username='testuser')
        print(f"✅ Test user 'testuser' already exists")
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=test_user, role='user')
        print(f"✅ Created test user: testuser")
    
    print("Test user created successfully!")
    print("Username: testuser")
    print("Password: testpass123")
    print("You can now test issue reporting with this user.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
