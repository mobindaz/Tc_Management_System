# Generated by Django 5.1.3 on 2025-01-14 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clerks', '0002_clerkaction_forwarded_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clerkaction',
            name='forwarded_by',
        ),
    ]
