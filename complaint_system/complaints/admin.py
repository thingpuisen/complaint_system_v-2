from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Complaint

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'contact', 'address')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('name', 'contact', 'address')}),
    )
    list_display = ['username', 'name', 'contact', 'email', 'is_staff']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['category', 'title', 'user', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status']
    ordering = ['-created_at']
