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

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
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

- **Database**: The project uses SQLite for development. For production, configure a PostgreSQL or MySQL database in `settings.py`
- **Media Files**: User-uploaded files are stored in the `media/` directory (not tracked in git)
- **Static Files**: Run `python manage.py collectstatic` after deployment
- **Environment Variables**: For production, set `DEBUG=False` and configure `SECRET_KEY`, database credentials, and other sensitive settings

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

