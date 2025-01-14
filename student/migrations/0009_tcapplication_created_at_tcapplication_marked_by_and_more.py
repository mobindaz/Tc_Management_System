# Generated by Django 5.1.3 on 2024-12-27 10:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_alter_tcapplication_options_alter_tcapplication_prn'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tcapplication',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tcapplication',
            name='marked_by',
            field=models.ForeignKey(blank=True, help_text="User who marked the application as 'Due'.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tc_marked_as_due', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tcapplication',
            name='rejected_by',
            field=models.ForeignKey(blank=True, help_text='The user who rejected the application.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tc_rejected_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='approved_by',
            field=models.ManyToManyField(blank=True, help_text='List of users who approved the application.', related_name='tc_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='due_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='tcapplication',
            name='pending_approval',
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='roll_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='tcapplication',
            name='pending_approval',
            field=models.ForeignKey(blank=True, help_text='The current user required to approve the application.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tc_pending_approval', to=settings.AUTH_USER_MODEL),
        ),
    ]
