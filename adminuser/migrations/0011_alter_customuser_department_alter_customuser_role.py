# Generated by Django 5.1.3 on 2025-01-02 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminuser', '0010_alter_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='department',
            field=models.CharField(blank=True, choices=[('CHE', 'COMPUTER HARDWARE ENGINEERING'), ('CE', 'CIVIL ENGINEERING'), ('ME', 'MECHANICAL ENGINEERING'), ('IE', 'INSTRUMENTATION ENGINEERING'), ('EE', 'ELECTRONICS ENGINEERING'), ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING'), ('nss', 'NSS'), ('ncc', 'NCC'), ('lab', 'Lab'), ('hostel', 'Hostel'), ('library', 'Library'), ('academics', 'Academics')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('student', 'Student'), ('hod', 'HOD'), ('tutor', 'Tutor'), ('staff', 'Staff'), ('nss', 'NSS'), ('ncc', 'NCC'), ('lab', 'Lab'), ('hostel', 'Hostel'), ('library', 'Library'), ('academics', 'Academics')], default='student', max_length=10),
        ),
    ]
