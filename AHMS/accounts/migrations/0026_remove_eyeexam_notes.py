# Generated by Django 5.0.1 on 2025-04-09 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_eyeexam'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eyeexam',
            name='notes',
        ),
    ]
