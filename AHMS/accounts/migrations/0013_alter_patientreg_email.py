# Generated by Django 5.0.1 on 2025-03-14 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_staffd_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientreg',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
