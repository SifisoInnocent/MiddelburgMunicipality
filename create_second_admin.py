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
    
    print("Creating second admin account...")
    
    # Create second admin user
    try:
        admin2 = User.objects.create_user(
            username='admin2',
            email='admin2@municipality.gov',
            password='admin123'
        )
        UserProfile.objects.create(user=admin2, role='admin')
        print(f"✅ Created second admin: admin2")
        print("✅ Multiple admin accounts are now allowed!")
        print("\n🔐 ADMIN LOGIN CREDENTIALS:")
        print("Admin 1 - Username: admin, Password: admin123")
        print("Admin 2 - Username: admin2, Password: admin123")
        print("\n🎯 Both can access: /admin-panel/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Django setup error: {e}")
    import traceback
    traceback.print_exc()
