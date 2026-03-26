import os
import sys
import django

sys.path.append('c:\\Users\\Admin\\Desktop\\municipal-helpdesk')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from issues.models import Issue

# Create test user and issue
try:
    test_user = User.objects.get(username='user1')
except User.DoesNotExist:
    test_user = User.objects.create_user(
        username='user1',
        email='user1@test.com',
        password='user123'
    )
    UserProfile.objects.create(user=test_user, role='user')

issue = Issue.objects.create(
    user=test_user,
    title='Test Water Leak',
    category='water',
    description='This is a test water leak issue.',
    location='123 Main Street',
    reference_number='TEST-001'
)

print(f"✅ Created test issue: {issue.reference_number}")
print("Now you can track this issue at: /track/TEST-001/")
