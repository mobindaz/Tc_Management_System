from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Set the role to 'admin' by default

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# Custom User Model

class CustomUser(AbstractUser):
    # Role choices for different users in the college
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('hod', 'HOD'),
        ('tutor', 'Tutor'),
        ('staff', 'Staff'),
        ('nss', 'NSS'),
        ('ncc', 'NCC'),
    ]

    DEPARTMENT_CHOICES = [
        ('CHE', 'COMPUTER HARDWARE ENGINEERING'),
        ('CE', 'CIVIL ENGINEERING'),
        ('ME', 'MECHANICAL ENGINEERING'),
        ('IE', 'INSTRUMENTATION ENGINEERING'),
        ('EE', 'ELECTRONICS ENGINEERING'),
        ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING'),
        ('nss', 'NSS'),
        ('ncc', 'NCC'),
    ]

    # General fields for all users
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)  # Applicable for department-specific users
    dob = models.DateField(blank=True, null=True)  # Date of Birth
    address = models.TextField(blank=True, null=True)  # Address
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Phone Number
    email = models.EmailField(unique=False,blank=True,null=True)  # Email is unique for all users
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


    # Student-specific fields
    prn = models.CharField(max_length=20, blank=True, null=True, unique=True)  # Unique PRN for students
    parent_name = models.CharField(max_length=100, blank=True, null=True)  # Parent/Guardian Name
    parent_contact = models.CharField(max_length=15, blank=True, null=True)  # Parent/Guardian Contact Number

    # Common MetaData
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for updates

    def __str__(self):
        return f"{self.username} ({self.role})"

