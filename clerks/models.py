from django.db import models
from django.conf import settings
from adminuser.models import CustomUser
from student.models import TCApplication

class ClerkAction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('due', 'Due'),
    ]

    tc_application = models.ForeignKey(TCApplication, on_delete=models.CASCADE, related_name="clerk_actions")
    clerk = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'clerk'})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.tc_application.id} - {self.status} by {self.clerk}"
