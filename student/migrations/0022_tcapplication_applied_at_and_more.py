# Generated by Django 5.1.3 on 2025-01-02 11:44

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0021_tcapplication_is_uploaded_due'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tcapplication',
            name='applied_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tcapplication',
            name='auto_approval_deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_approval_enabled', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
