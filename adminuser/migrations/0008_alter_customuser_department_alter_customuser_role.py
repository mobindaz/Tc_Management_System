# Generated by Django 5.1.3 on 2024-12-31 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminuser', '0007_alter_customuser_department_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='department',
            field=models.CharField(blank=True, choices=[('CHE', 'COMPUTER HARDWARE ENGINEERING'), ('CE', 'CIVIL ENGINEERING'), ('ME', 'MECHANICAL ENGINEERING'), ('IE', 'INSTRUMENTATION ENGINEERING'), ('EE', 'ELECTRONICS ENGINEERING'), ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING'), ('nss', 'NSS'), ('ncc', 'NCC')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('student', 'Student'), ('hod', 'HOD'), ('tutor', 'Tutor'), ('staff', 'Staff'), ('nss', 'NSS'), ('ncc', 'NCC')], default='student', max_length=10),
        ),
    ]