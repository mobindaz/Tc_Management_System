from django.db import models
from django.conf import settings

class AutoApprovalSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auto_approval_enabled = models.BooleanField(default=False)

 