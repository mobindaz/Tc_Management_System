# Generated by Django 5.1.3 on 2024-12-31 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminuser', '0008_alter_customuser_department_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]