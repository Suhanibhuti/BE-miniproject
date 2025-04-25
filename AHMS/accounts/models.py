from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

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
    email = models.EmailField(null=True, blank=True)
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
    
    
class PatientReport(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='patient_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name 
    
    
    
    
class StaffD(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', default=1)
    full_name = models.CharField(max_length=100)
    email = models.EmailField( null=True, blank=True)
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
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    doctor = models.ForeignKey(StaffD, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        
        
class NurseReg(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)  # Allow null and blank
    gender = models.CharField(max_length=10,  null=True, blank=True)
    age = models.IntegerField()
    department = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return self.full_name
    
    
class DoctorComment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_comments')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments_given')
    comment = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.doctor.username} for {self.patient.username}"
    
    
class Prescription(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescribed_by')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    timing = models.CharField(max_length=50)  # e.g., "1-1-1" or "1-0-1"
    before_after_food = models.CharField(max_length=10, choices=[('before', 'Before Food'), ('after', 'After Food'), ('none', 'None')])
    prescribed_at = models.DateTimeField(auto_now_add=True)
    reminders_set = models.BooleanField(default=False)  # New field to track toggle state

    def __str__(self):
        return f"{self.medicine_name} for {self.patient.username} (Prescribed by: {self.doctor.username})"
    
    
    
class WeightTracking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_tracking')
    department = models.CharField(max_length=50, default='Dialysis')  # Add department field
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # Weight in kg
    date = models.DateField(auto_now_add=True)  # Date of the weight entry

    def __str__(self):
        return f"{self.patient.username} - {self.weight} kg on {self.date}"

class DialysisTubing(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dialysis_tubing')
    department = models.CharField(max_length=50, default='Dialysis')  # Add department field
    tubing_count = models.PositiveIntegerField()  # Tubing count (e.g., 1/4)
    date = models.DateTimeField(auto_now_add=True)  # Date and time of the tubing entry

    def __str__(self):
        return f"{self.patient.username} - {self.tubing_count}/4 on {self.date}"

class WaterIntake(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_intake')
    department = models.CharField(max_length=50, default='Dialysis')  # Add department field
    amount = models.PositiveIntegerField()  # Water intake in ml
    date = models.DateTimeField(auto_now_add=True)  # Date and time of the water intake entry

    def __str__(self):
        return f"{self.patient.username} - {self.amount} ml on {self.date}"
    
    
class EyeExam(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eye_exams')
    exam_date = models.DateField()
    department = models.CharField(max_length=50, default='Eyecare')
    
    # Right eye measurements
    right_sph = models.DecimalField(max_digits=5, decimal_places=2)
    right_cyl = models.DecimalField(max_digits=5, decimal_places=2)
    right_axis = models.IntegerField()
    right_prism = models.CharField(max_length=20, blank=True, null=True)
    
    # Left eye measurements
    left_sph = models.DecimalField(max_digits=5, decimal_places=2)
    left_cyl = models.DecimalField(max_digits=5, decimal_places=2)
    left_axis = models.IntegerField()
    left_prism = models.CharField(max_length=20, blank=True, null=True)
    
    
    class Meta:
        ordering = ['-exam_date']  # Newest exams first
    
    def __str__(self):
        return f"Eye Exam for {self.patient} on {self.exam_date}"
    
    
class BloodPressureReading(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_pressure_readings')
    department = models.CharField(max_length=50, default='Cardiology')
    record_date = models.DateField(auto_now_add=True) 
    systolic = models.PositiveIntegerField()
    diastolic = models.PositiveIntegerField()
    pulse = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default='Normal')
    
    class Meta:
        ordering = ['-record_date']
       
    def __str__(self):
        return f"BP for {self.patient} on {self.record_date}"
    
    
class CholesterolReading(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cholesterol_readings')
    department = models.CharField(max_length=50, default='Cardiology')
    record_date = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField()  # mg/dL
    ldl = models.PositiveIntegerField()    # mg/dL
    hdl = models.PositiveIntegerField()    # mg/dL
    triglycerides = models.PositiveIntegerField()  # mg/dL
    status = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-record_date']
        verbose_name = 'Cholesterol Reading'
        verbose_name_plural = 'Cholesterol Readings'
       
    def __str__(self):
        return f"Cholesterol {self.total}/{self.ldl}/{self.hdl} for {self.patient}"
    
    
class ECGReading(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ecg_readings')
    record_date = models.DateTimeField(auto_now_add=True)
    heart_rate = models.PositiveSmallIntegerField()  # bpm
    pr_interval = models.PositiveSmallIntegerField()  # ms
    qrs_duration = models.PositiveSmallIntegerField()  # ms
    qt_interval = models.PositiveSmallIntegerField()  # ms
    qtc = models.PositiveSmallIntegerField()  # ms
    
    @property
    def rhythm(self):
        """Automatically determine rhythm with severity built into the name"""
        if self.qtc > 500:
            return "⚠️ Prolonged QT (Critical)"
        elif self.heart_rate > 140:
            return "⚠️ Severe Tachycardia"
        elif self.heart_rate > 100:
            return "↑ Tachycardia"
        elif self.heart_rate < 40:
            return "⚠️ Severe Bradycardia"
        elif self.heart_rate < 60:
            return "↓ Bradycardia"
        elif self.pr_interval > 200:
            return "1st Degree AV Block"
        elif self.qrs_duration > 120:
            return "Bundle Branch Block"
        return "Normal Sinus Rhythm"
    
    
    @property
    def health_score(self):
        """Calculate a simple health score (0-100)"""
        score = 100
        
        # Heart rate deductions
        if self.heart_rate > 140 or self.heart_rate < 40:
            score -= 50
        elif self.heart_rate > 120 or self.heart_rate < 50:
            score -= 30
        elif self.heart_rate > 100 or self.heart_rate < 60:
            score -= 15
            
        # QTc deductions
        if self.qtc > 500:
            score -= 40
        elif self.qtc > 450:
            score -= 20
            
        # Other intervals
        if self.pr_interval > 200:
            score -= 15
        if self.qrs_duration > 120:
            score -= 15
            
        return max(0, min(100, score))
    
    @property
    def health_status(self):
        """Get a simple health status"""
        score = self.health_score
        if score >= 80:
            return ('good', 'Healthy')
        elif score >= 50:
            return ('fair', 'Fair')
        else:
            return ('poor', 'Needs Attention')

    class Meta:
        ordering = ['-record_date']
        verbose_name = 'ECG Reading'