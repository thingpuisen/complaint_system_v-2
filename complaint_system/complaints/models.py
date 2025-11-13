from django.db import models
from django.contrib.auth.models import AbstractUser

DEPARTMENT_CHOICES = [
    ('admin', 'Central Administration'),
    ('power', 'Power & Electricity'),
    ('health', 'Public Health & Engineering'),
    ('works', 'Public Works'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

class User(AbstractUser):
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=15)
    address = models.TextField()
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.username

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('electricity', 'Electricity'),
        ('road', 'Road'),
        ('sanitation', 'Sanitation'),
        ('water_supply', 'Water Supply'),
        ('others', 'Others'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='complaint_photos/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default='')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title} - {self.user.username}"