# Generated by Django 5.0.1 on 2025-03-15 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_nursereg_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffd',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
