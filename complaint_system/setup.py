"""
Quick setup script for the Complaint Management System.
Run this after cloning the repository to set up the project.
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    print("="*60)
    print("Complaint Management System - Setup Script")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Create virtual environment
    if not os.path.exists("venv"):
        print("\nCreating virtual environment...")
        if sys.platform == "win32":
            run_command("python -m venv venv", "Creating virtual environment")
            activate_script = "venv\\Scripts\\activate"
        else:
            run_command("python3 -m venv venv", "Creating virtual environment")
            activate_script = "venv/bin/activate"
        
        print(f"\n✓ Virtual environment created!")
        print(f"  To activate it, run:")
        if sys.platform == "win32":
            print(f"    venv\\Scripts\\activate")
        else:
            print(f"    source venv/bin/activate")
    else:
        print("\n✓ Virtual environment already exists")
    
    # Step 2: Install dependencies
    print("\n" + "="*60)
    print("IMPORTANT: Please activate your virtual environment first!")
    print("="*60)
    if sys.platform == "win32":
        print("Windows: venv\\Scripts\\activate")
    else:
        print("Linux/Mac: source venv/bin/activate")
    
    response = input("\nHave you activated the virtual environment? (y/n): ")
    if response.lower() != 'y':
        print("\nPlease activate the virtual environment and run this script again.")
        sys.exit(0)
    
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\nFailed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        print("\nFailed to run migrations. Please check the error above.")
        sys.exit(1)
    
    # Step 4: Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("\nWarning: Failed to collect static files. You may need to run this manually.")
    
    # Step 5: Create superuser
    print("\n" + "="*60)
    print("Create a superuser account")
    print("="*60)
    print("You'll need a superuser to access the Django admin panel.")
    response = input("Do you want to create a superuser now? (y/n): ")
    if response.lower() == 'y':
        run_command("python manage.py createsuperuser", "Creating superuser")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Make sure your virtual environment is activated")
    print("2. Run: python manage.py runserver")
    print("3. Open http://127.0.0.1:8000 in your browser")
    print("\nFor authority staff accounts:")
    print("- Go to Django admin: http://127.0.0.1:8000/admin")
    print("- Create staff users and assign them to departments")
    print("- Then they can login at: http://127.0.0.1:8000/authority/")

if __name__ == "__main__":
    main()

