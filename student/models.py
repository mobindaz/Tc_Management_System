from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError



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
    department = models.CharField(choices=DEPARTMENT_CHOICES, max_length=50)
    prn = models.CharField(max_length=20, unique=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)
    due_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_uploaded_due = models.BooleanField(default=False)

    # Add method to move applications to main due list
    def add_to_due_list(self, user, due_reason='', is_uploaded_due=False):
        self.due_list.add(user)
        self.due_reason = due_reason
        self.is_uploaded_due = is_uploaded_due
        self.save()

    due_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="due_applications",
        blank=True,
    )
    # Track users involved in the approval process
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

    def approve(self, user):
        """
        Mark application as approved by the given user.
        """
        if user in self.pending_approval.all():
            self.approved_by.add(user)
            self.pending_approval.remove(user)
            # Update status if all approvals are complete
            if self.is_fully_approved():
                self.status = 'approved'
            self.save()
        else:
            raise ValidationError("You are not authorized to approve this application.")

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

    def add_to_due_list(self, user, due_reason=None):
        """
        Add a user to the due list and update the status to 'due'.
        """
        self.due_list.add(user)
        self.status = 'due'
        if due_reason:
            self.due_reason = due_reason
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_department_display()}) - {self.status}"

    class Meta:
        verbose_name = "Transfer Certificate Application"
        verbose_name_plural = "Transfer Certificate Applications"
        ordering = ['-updated_at']
