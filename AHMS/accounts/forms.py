from django import forms
from .models import PatientReg,PatientReport,DoctorComment,WaterIntake,WeightTracking,DialysisTubing
from django.core.exceptions import ValidationError

class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientReg
        exclude = ['user']  
        fields = [
            'full_name', 'date_of_birth', 'email', 'mobile_number', 'gender',
            'age', 'blood_group', 'marital_status', 'address',
            'emergency_contact_name', 'emergency_contact_number', 'occupation',
            'habits', 'medical_history', 'disease'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),  # Custom widget for date fields
            'marital_status': forms.Select(),
        }


class PatientReportForm(forms.ModelForm):
    class Meta:
        model = PatientReport
        fields = ['file']


class DoctorCommentForm(forms.ModelForm):
    class Meta:
        model = DoctorComment
        fields = ['comment']
        
        
class WeightTrackingForm(forms.ModelForm):
    class Meta:
        model = WeightTracking
        fields = ['weight']

class DialysisTubingForm(forms.ModelForm):
    class Meta:
        model = DialysisTubing
        fields = ['tubing_count']

class WaterIntakeForm(forms.ModelForm):
    class Meta:
        model = WaterIntake
        fields = ['amount']
