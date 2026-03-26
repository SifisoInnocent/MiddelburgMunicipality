#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
    
    # Test models
    from accounts.models import UserProfile
    from issues.models import Issue
    
    print(f"✅ Models imported successfully!")
    print(f"✅ UserProfiles: {UserProfile.objects.count()} existing")
    print(f"✅ Issues: {Issue.objects.count()} existing")
    
    # Test admin functionality
    admin_count = UserProfile.objects.filter(role='admin').count()
    print(f"✅ Admin accounts: {admin_count}")
    
    print("🚀 Ready to run server!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
