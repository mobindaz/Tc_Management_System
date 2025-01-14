from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser

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
        ('lab', 'Lab'),
        ('hostel', 'Hostel'),
        ('library', 'Library'),
        ('academics', 'Academics'),
        ('clerks', 'Clerks'),
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
        ('lab', 'Lab'),
        ('hostel', 'Hostel'),
        ('library', 'Library'),
        ('academics', 'Academics'),
        ('clerks', 'Clerks'),
    ]

    # General fields for all users
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=False, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    auto_approval_enabled = models.BooleanField(default=False) 
    # Student-specific fields
    prn = models.CharField(max_length=20, blank=True, null=True, unique=True)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_contact = models.CharField(max_length=15, blank=True, null=True)

    # Common MetaData
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def clean(self):
        super().clean()  # Ensure parent validation is performed

        # Ensure PRN is mandatory for students
        if self.role == 'student' and not self.prn:
            raise ValidationError({'prn': 'PRN is mandatory for student roles.'})
        

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method for validation
        super().save(*args, **kwargs)
