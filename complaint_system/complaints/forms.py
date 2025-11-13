from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Complaint

# Validators
phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{9,20}$',
    message="Contact number must be 9-20 digits. Can include +, spaces, dashes, and parentheses."
)

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]+$',
    message="Username can only contain letters, numbers, and underscores."
)

name_validator = RegexValidator(
    regex=r'^[a-zA-Z\s]+$',
    message="Name can only contain letters and spaces."
)

class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=200, 
        required=True,
        validators=[name_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'minlength': '2',
        }),
        help_text="Enter your full name (letters and spaces only, minimum 2 characters)"
    )
    
    contact = forms.CharField(
        max_length=15, 
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'placeholder': 'Contact Number (e.g., +1234567890)',
            'pattern': r'\+?1?\d{9,15}',
        }),
        help_text="Enter a valid contact number (9-15 digits, optionally starting with +)"
    )
    
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Your address',
            'minlength': '10',
        }), 
        required=True,
        help_text="Enter your complete address (minimum 10 characters)"
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[username_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'minlength': '3',
            'maxlength': '150',
        }),
        help_text="Required. 3-150 characters. Letters, numbers and underscores only."
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
        help_text="Password must be at least 8 characters and contain uppercase, lowercase, number, and symbol."
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        }),
        help_text="Enter the same password as before, for verification."
    )
    
    class Meta:
        model = User
        fields = ['username', 'name', 'contact', 'address', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) < 3:
                raise ValidationError("Username must be at least 3 characters long.")
            if len(username) > 150:
                raise ValidationError("Username must be 150 characters or fewer.")
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                raise ValidationError("A user with this username already exists.")
        return username
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Name must be at least 2 characters long.")
            if len(name) > 200:
                raise ValidationError("Name must be 200 characters or fewer.")
        return name
    
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact:
            # Count digits (excluding +, spaces, dashes, etc.)
            digit_count = sum(1 for c in contact if c.isdigit())
            if digit_count < 9 or digit_count > 15:
                raise ValidationError("Contact number must contain 9-15 digits.")
            # Check if contact already exists (normalize for comparison - digits only)
            normalized_contact = ''.join(filter(str.isdigit, contact))
            # Check all existing users' contacts (normalized)
            all_users = User.objects.all()
            for user in all_users:
                user_contact_normalized = ''.join(filter(str.isdigit, user.contact))
                if user_contact_normalized == normalized_contact:
                    raise ValidationError("A user with this contact number already exists.")
        return contact
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            address = address.strip()
            if len(address) < 10:
                raise ValidationError("Address must be at least 10 characters long.")
        return address
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            if not any(c.isupper() for c in password1):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not any(c.islower() for c in password1):
                raise ValidationError("Password must contain at least one lowercase letter.")
            if not any(c.isdigit() for c in password1):
                raise ValidationError("Password must contain at least one number.")
            if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password1):
                raise ValidationError("Password must contain at least one symbol (!@#$%^&*(),.?\":{}|<>)")
        return password1

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'priority', 'photo']
        widgets = {
            'category': forms.Select(),
            'title': forms.TextInput(attrs={'maxlength': 200}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'priority': forms.Select(),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'photo':
                continue
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} complaint-input".strip()

class ComplaintAdminForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_department', 'priority']
        widgets = {
            'status': forms.Select(),
            'assigned_department': forms.Select(),
            'priority': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing} complaint-input".strip()