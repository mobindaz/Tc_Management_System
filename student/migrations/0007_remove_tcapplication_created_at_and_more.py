# Generated by Django 5.1.3 on 2024-12-26 11:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_tcapplication_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tcapplication',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='approved_by',
            field=models.ManyToManyField(blank=True, related_name='tc_approvals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='department',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='due_reason',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='pending_approval',
            field=models.ManyToManyField(blank=True, related_name='tc_pending_approvals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='prn',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='tcapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('due', 'Due')], default='pending', max_length=10),
        ),
    ]