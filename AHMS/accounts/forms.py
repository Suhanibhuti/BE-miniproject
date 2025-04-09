from django import forms
from .models import PatientReg,PatientReport,DoctorComment,WaterIntake,WeightTracking,DialysisTubing,EyeExam
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



class EyeExamForm(forms.ModelForm):
    class Meta:
        model = EyeExam
        fields = [
            'exam_date',
            'right_sph', 'right_cyl', 'right_axis', 'right_prism',
            'left_sph', 'left_cyl', 'left_axis', 'left_prism'
        ]
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'right_sph': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'right_cyl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'right_axis': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '180'}),
            'right_prism': forms.TextInput(attrs={'class': 'form-control'}),
            'left_sph': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'left_cyl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'left_axis': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '180'}),
            'left_prism': forms.TextInput(attrs={'class': 'form-control'}),
        }