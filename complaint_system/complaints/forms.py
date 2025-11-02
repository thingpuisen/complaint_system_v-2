from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Complaint

class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True)
    contact = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'name', 'contact', 'address', 'password1', 'password2']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }