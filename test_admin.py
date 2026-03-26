#!/usr/bin/env python
import os
import sys
import django

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    from issues.models import Issue
    
    print("=== Testing Admin Dashboard ===")
    
    # Create test admin if none exists
    admin_count = UserProfile.objects.filter(role='admin').count()
    print(f"Current admin count: {admin_count}")
    
    if admin_count == 0:
        print("Creating test admin user...")
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        UserProfile.objects.create(user=admin_user, role='admin')
        print("✅ Test admin created: username=admin, password=admin123")
    
    # Create test regular user
    user_count = User.objects.count()
    if user_count == 1:
        print("Creating test regular user...")
        regular_user = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='user123'
        )
        UserProfile.objects.create(user=regular_user, role='user')
        print("✅ Test user created: username=user1, password=user123")
    
    # Create test issues
    print("Creating test issues...")
    admin_user = User.objects.get(username='admin')
    regular_user = User.objects.get(username='user1')
    
    issue1 = Issue.objects.create(
        user=regular_user,
        title='Water Leak on Main Street',
        category='water',
        description='Major water leak reported',
        location='123 Main Street',
        reference_number='TEST-001'
    )
    
    issue2 = Issue.objects.create(
        user=regular_user,
        title='Pothole on Oak Avenue',
        category='pothole',
        description='Large pothole causing traffic issues',
        location='456 Oak Avenue',
        reference_number='TEST-002'
    )
    
    print(f"✅ Created {Issue.objects.count()} test issues")
    
    # Test admin check function
    from issues.views import is_admin
    print(f"✅ Admin check for admin_user: {is_admin(admin_user)}")
    print(f"✅ Admin check for regular_user: {is_admin(regular_user)}")
    
    print("\n=== Ready for Testing ===")
    print("1. Go to: http://127.0.0.1:8000")
    print("2. Login as admin: username=admin, password=admin123")
    print("3. Access admin dashboard at: http://127.0.0.1:8000/admin/")
    print("4. Try updating issue statuses!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
