from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Complaint

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'contact', 'address', 'department')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('name', 'contact', 'address', 'department')}),
    )
    list_display = ['username', 'name', 'contact', 'department', 'email', 'is_staff']
    list_filter = BaseUserAdmin.list_filter + ('department',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['category', 'title', 'user', 'assigned_department', 'priority', 'status', 'created_at']
    list_filter = ['category', 'status', 'assigned_department', 'priority', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status', 'assigned_department', 'priority']
    ordering = ['-created_at']
