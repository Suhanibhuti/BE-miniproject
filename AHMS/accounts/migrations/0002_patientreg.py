# Generated by Django 5.0.1 on 2025-02-09 15:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientReg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mobile_number', models.CharField(max_length=15)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], max_length=10)),
                ('age', models.PositiveIntegerField()),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=3)),
                ('marital_status', models.CharField(choices=[('Single', 'Single'), ('Married', 'Married')], max_length=10)),
                ('address', models.TextField()),
                ('emergency_contact_name', models.CharField(max_length=100)),
                ('emergency_contact_number', models.CharField(max_length=15)),
                ('occupation', models.CharField(max_length=100)),
                ('habits', models.CharField(choices=[('Smoke', 'Smoke'), ('Drink', 'Drink'), ('Both', 'Both'), ('None', 'None')], max_length=20)),
                ('medical_history', models.TextField(blank=True, null=True)),
                ('disease', models.CharField(blank=True, choices=[('Diabetes', 'Diabetes'), ('Blood Pressure', 'Blood Pressure'), ('Allergy', 'Allergy'), ('Others', 'Others')], max_length=50, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patients', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
