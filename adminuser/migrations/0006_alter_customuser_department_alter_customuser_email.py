# Generated by Django 5.1.3 on 2024-12-28 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminuser', '0005_remove_customuser_temporary_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='department',
            field=models.CharField(blank=True, choices=[('CHE', 'COMPUTER HARDWARE ENGINEERING'), ('CE', 'CIVIL ENGINEERING'), ('ME', 'MECHANICAL ENGINEERING'), ('IE', 'INSTRUMENTATION ENGINEERING'), ('EE', 'ELECTRONICS ENGINEERING'), ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]