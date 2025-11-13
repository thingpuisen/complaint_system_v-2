# Complaint Management System

A Django-based complaint management system with separate portals for citizens and authority departments.

## Features

- **Citizen Portal**: Users can register, login, submit complaints, and track their complaint status
- **Authority Portal**: Department-based dashboards for managing complaints
  - Central Administration (Admin) - Full system oversight
  - Power & Electricity Department
  - Public Health & Engineering Department
  - Public Works Department
- **JWT Authentication**: Secure token-based authentication for authority staff
- **Department-based Access Control**: Strict access control ensuring staff can only access their assigned department
- **Complaint Management**: Track, filter, and manage complaints with status updates and priority assignment

## Technology Stack

- Django 5.2.7
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Pillow (for image handling)
- SQLite (development database)

## Installation

### Quick Setup (Automated)

1. **Clone the repository**
   ```bash
   git clone https://github.com/thingpuisen/complaint_system_v-2.git
   cd complaint_system
   ```

2. **Run the setup script** (optional but recommended)
   ```bash
   python setup.py
   ```
   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Run database migrations
   - Collect static files
   - Help you create a superuser

### Manual Setup

If you prefer to set up manually:

1. **Clone the repository**
   ```bash
   git clone https://github.com/thingpuisen/complaint_system_v-2.git
   cd complaint_system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations** (creates the database)
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (for Django admin access)
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Citizen Portal: http://127.0.0.1:8000/
   - Authority Portal: http://127.0.0.1:8000/authority/
   - Django Admin: http://127.0.0.1:8000/admin/

### Setting Up Authority Staff Accounts

After creating a superuser, you need to create staff accounts for authority departments:

1. Go to Django admin: http://127.0.0.1:8000/admin/
2. Navigate to **Users** section
3. Create new users or edit existing ones
4. For each authority staff member:
   - Check **Staff status**
   - Select their **Department** (admin, power, health, or works)
   - Set a secure password
5. They can now login at: http://127.0.0.1:8000/authority/

## Project Structure

```
complaint_system/
├── complaint_system/      # Main project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── complaints/            # Main app
│   ├── models.py         # User and Complaint models
│   ├── views.py          # View logic
│   ├── forms.py          # Django forms
│   ├── jwt_auth.py       # JWT authentication utilities
│   ├── templates/        # HTML templates
│   ├── static/           # Static files (CSS, JS)
│   └── migrations/       # Database migrations
├── media/                 # User-uploaded files (not in git)
├── staticfiles/           # Collected static files (not in git)
└── db.sqlite3            # SQLite database (not in git)
```

## Usage

### For Citizens

1. Register a new account at `/register/`
2. Login at `/login/`
3. Submit complaints at `/submit-complaint/`
4. View your complaints at `/my-complaints/`

### For Authority Staff

1. Navigate to `/authority/` to select your department
2. Login with your staff credentials
3. Access your department dashboard to manage complaints
4. Admin users can view and manage all complaints

## Important Notes

- **Database**: The project uses SQLite for development. When you clone the repo, you'll get a fresh empty database. Run `python manage.py migrate` to create the database structure.
- **Media Files**: User-uploaded files are stored in the `media/` directory (created automatically, not in git)
- **Static Files**: The `staticfiles/` directory is generated automatically when you run `collectstatic` (not in git)
- **Fresh Install**: When cloning on a new system, you'll need to:
  - Create a new database (via migrations)
  - Create a superuser account
  - Create staff accounts for authority departments
- **Production**: For production deployment, set `DEBUG=False` in `settings.py` and configure `SECRET_KEY`, database credentials, and other sensitive settings

## Security Features

- JWT-based authentication for authority staff
- Department-based access control
- CSRF protection
- Secure password handling
- HTTPOnly cookies for JWT tokens

## License

[Add your license here]

## Author

[Add your name/contact information here]

