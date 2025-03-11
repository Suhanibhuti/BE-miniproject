from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
        (NURSE, 'Nurse'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)
    

class PatientReg(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    age = models.PositiveIntegerField()
    blood_group = models.CharField(max_length=5)
    marital_status = models.CharField(max_length=10, choices=[('single', 'Single'), ('married', 'Married')])

    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    occupation = models.CharField(max_length=100)
    habits = models.CharField(max_length=50, blank=True)
    medical_history = models.TextField(null=False, default="None")
    disease = models.CharField(max_length=50, null=False, default="None")

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
    
    
class StaffD(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', default=1)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    age = models.PositiveIntegerField()
    department = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    years_of_experience = models.CharField(max_length=10)

    def __str__(self):
        return self.full_name

class WorkingHour(models.Model):
    staff = models.ForeignKey(StaffD, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.staff.full_name} - {self.start_time} to {self.end_time}"
    
class Appointment(models.Model):
    doctor = models.ForeignKey(StaffD, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')