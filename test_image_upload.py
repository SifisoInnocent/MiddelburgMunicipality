#!/usr/bin/env python
"""
Test script to verify image upload functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipal_helpdesk.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from issues.models import Issue, IssueForm
from django.contrib.auth.models import User

def test_image_upload():
    print("🧪 Testing Image Upload Functionality")
    print("=" * 50)
    
    # Check if media directory exists
    media_path = 'media/issues'
    if os.path.exists(media_path):
        print(f"✅ Media directory exists: {media_path}")
    else:
        print(f"❌ Media directory missing: {media_path}")
        return False
    
    # Check model field
    try:
        image_field = Issue._meta.get_field('image')
        print(f"✅ Image field found: {image_field}")
        print(f"   - Field type: {type(image_field).__name__}")
        print(f"   - Upload to: {image_field.upload_to}")
        print(f"   - Blank: {image_field.blank}")
        print(f"   - Null: {image_field.null}")
    except Exception as e:
        print(f"❌ Image field error: {e}")
        return False
    
    # Check form field
    try:
        form = IssueForm()
        if 'image' in form.fields:
            print("✅ Image field found in form")
        else:
            print("❌ Image field missing from form")
            return False
    except Exception as e:
        print(f"❌ Form error: {e}")
        return False
    
    # Create a test image file
    try:
        # Create a simple test image (1x1 pixel PNG)
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
        test_image = SimpleUploadedFile(
            "test_image.png",
            test_image_content,
            content_type="image/png"
        )
        print("✅ Test image created")
    except Exception as e:
        print(f"❌ Test image creation failed: {e}")
        return False
    
    # Test form validation with image
    try:
        form_data = {
            'title': 'Test Issue with Image',
            'category': 'water',
            'description': 'This is a test issue with an image attachment.',
            'location': 'Test Location',
        }
        
        form = IssueForm(data=form_data, files={'image': test_image})
        if form.is_valid():
            print("✅ Form validation passed with image")
            
            # Check if image is in cleaned data
            if 'image' in form.cleaned_data:
                print("✅ Image found in cleaned data")
                print(f"   - Image name: {form.cleaned_data['image'].name}")
                print(f"   - Image size: {form.cleaned_data['image'].size} bytes")
            else:
                print("❌ Image not found in cleaned data")
                return False
        else:
            print(f"❌ Form validation failed: {form.errors}")
            return False
    except Exception as e:
        print(f"❌ Form validation error: {e}")
        return False
    
    print("\n🎉 Image Upload Functionality Test: PASSED")
    print("=" * 50)
    return True

if __name__ == '__main__':
    success = test_image_upload()
    sys.exit(0 if success else 1)
