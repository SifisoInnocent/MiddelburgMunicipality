#!/usr/bin/env python3
"""
Setup script for Municipal Helpdesk System
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ ERROR!")
        print("Error:", e.stderr)
        return False

def main():
    """Main setup function"""
    print("🏛️ Municipal Helpdesk Setup")
    print("This script will set up the complete helpdesk system")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Failed to install dependencies. Please install manually:")
        print("pip install Django>=4.2.0,<5.0.0 Pillow>=9.0.0")
        return False
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        return False
    
    # Apply migrations
    if not run_command("python manage.py migrate", "Applying database migrations"):
        return False
    
    # Create superuser (optional)
    print("\n" + "="*50)
    print("Create admin user? (y/n): ", end="")
    create_admin = input().lower().strip()
    
    if create_admin == 'y':
        run_command("python manage.py createsuperuser", "Creating admin user")
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("Warning: Static files collection failed (may be okay for development)")
    
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    print("To start the server:")
    print("python manage.py runserver")
    print("\nThen visit: http://127.0.0.1:8000")
    print("Admin panel: http://127.0.0.1:8000/admin")
    print("="*50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
