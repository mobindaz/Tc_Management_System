# Generated by Django 5.1.3 on 2024-12-26 11:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_remove_tcapplication_approvals_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='tcapplication',
            name='approved_by',
            field=models.ManyToManyField(blank=True, related_name='tc_approvals', to=settings.AUTH_USER_MODEL),
        ),
    ]