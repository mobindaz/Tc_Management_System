from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from adminuser.models import CustomUser


class TCApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('due', 'Due'),
    ]

    DEPARTMENT_CHOICES = [
        ('CHE', 'COMPUTER HARDWARE ENGINEERING'),
        ('CE', 'CIVIL ENGINEERING'),
        ('ME', 'MECHANICAL ENGINEERING'),
        ('IE', 'INSTRUMENTATION ENGINEERING'),
        ('EE', 'ELECTRONICS ENGINEERING'),
        ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING'),
    ]

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    department = models.CharField(choices=DEPARTMENT_CHOICES, max_length=50, null=True, blank=True)
    prn = models.CharField(max_length=20, unique=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)
    due_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_uploaded_due = models.BooleanField(default=False)
    forwarded_to_clerk = models.BooleanField(default=False) 
    
    forwarded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name='forwarded_applications')

    # Relations for approval workflow
    due_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="due_applications",
        blank=True,
    )
    pending_approval = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tc_pending_approvals",
        blank=True,
        help_text="Users who are required to approve this application."
    )
    approved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tc_approvals",
        blank=True,
        help_text="Users who have approved this application."
    )
    rejected_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tc_rejections",
        blank=True,
        help_text="Users who have rejected this application."
    )
    due_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tc_due_lists",
        blank=True,
        help_text="Users who have flagged this application as due."
    )

    def clean(self):
        """
        Ensure due reason is provided when the status is 'due'.
        """
        if self.status == 'due' and not self.due_reason:
            raise ValidationError("A due reason is required when the status is 'due'.")

    def is_fully_approved(self):
        """
        Check if all pending approvals are completed.
        """
        return not self.pending_approval.exists()

    def approve(self, user=None, auto=False):
        """
        Mark application as approved.
        """
        if auto:
            self.status = 'approved'
        elif user and user in self.pending_approval.all():
            self.approved_by.add(user)
            self.pending_approval.remove(user)
            if self.is_fully_approved():
                self.status = 'approved'
        else:
            raise ValidationError("You are not authorized to approve this application.")
        self.save()

    def reject(self, user):
        """
        Mark application as rejected by the given user.
        """
        if user in self.pending_approval.all():
            self.rejected_by.add(user)
            self.pending_approval.remove(user)
            self.status = 'rejected'
            self.save()
        else:
            raise ValidationError("You are not authorized to reject this application.")

    def add_to_due_list(self, user, due_reason, is_uploaded_due=False):
        self.status = "Due"
        self.due_reason = due_reason
        self.is_uploaded_due = is_uploaded_due
        self.due_list.add(user)
        self.save()
    

    def __str__(self):
        return f"{self.name} ({self.get_department_display()}) - {self.status}"

    class Meta:
        verbose_name = "Transfer Certificate Application"
        verbose_name_plural = "Transfer Certificate Applications"
        ordering = ['-updated_at']

# Auto-approval time (add a field to store deadline)
    

class UploadedDueList(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    prn = models.CharField(max_length=20, unique=True)
    due_reason = models.TextField(default="No reason provided")
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="uploaded_due_lists",
        null=True,  
        blank=True
    )

    def get_due_list_prns(self):
        """Fetch all PRNs from the Due List."""
        return self.due_list.values_list('prn', flat=True)
    
    def __str__(self):
        return f"{self.prn} - {self.due_reason}"

