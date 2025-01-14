from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'role', 'department', 'prn', 'is_superuser')
    
    # Fields to use for search functionality
    search_fields = ('username', 'email', 'prn', 'department')
    
    # Filter options in the right sidebar
    list_filter = ('role', 'department', 'is_staff', 'is_superuser')
    
    # Fieldsets for the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'department', 'prn', 'profile_picture'),
        }),
    )
    
    # Fields to include when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'department', 'prn', 'profile_picture'),
        }),
    )
