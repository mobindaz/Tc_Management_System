# Generated by Django 5.1.3 on 2025-01-14 10:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0031_tcapplication_forwarded_to_clerk'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tcapplication',
            name='forwarded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forwarded_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
