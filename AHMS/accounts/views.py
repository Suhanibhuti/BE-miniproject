from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User,PatientReg,StaffD,WorkingHour,Appointment,NurseReg,PatientReport,DoctorComment,Prescription,WeightTracking,WaterIntake,DialysisTubing,EyeExam,BloodPressureReading,CholesterolReading,ECGReading
from .forms import PatientForm,PatientReportForm,DoctorCommentForm,WeightTrackingForm,WaterIntakeForm,DialysisTubingForm,EyeExamForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .utils import email
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Count,Sum
from django.db.models.functions import TruncDate
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.views.decorators.http import require_POST
from django.db.models.functions import TruncWeek

from django.core.mail import send_mail
from django.urls import reverse

from .models import User 

def logoutp(request):
    logout(request)    
    return redirect('login_p')

def logouts(request):
    logout(request)    
    return redirect('staff_login')

def basestaff(request):
    return render(request, 'accounts/basestaff.html')

def landing(request):
    return render(request, 'accounts/landing.html')

# Create your views here.

# def patient_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None and user.role == User.PATIENT:
#             login(request, user)
#             return redirect('patient_dashboard')
#         else:
#             return render(request, 'accounts/patient_login.html', {'error': 'Invalid credentials or not a patient'})
#     return render(request, 'accounts/login.html')

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        print(f"Username: {username}, Password: {password}")

        if user is not None:
            if user.role == 'doctor':
                login(request, user)
                return redirect('staff_dash')
            elif user.role == 'nurse':
                login(request, user)
                return redirect('nurse_dash')
            elif user.role == 'admin':
                login(request, user)
                return redirect('admin_dash')
        else:
            # Check if the user exists
            try:
                user = User.objects.get(username=username)
                # If user exists but password is incorrect
                messages.error(request, 'Incorrect password. Please try again.')
            except User.DoesNotExist:
                # If user does not exist
                messages.error(request, 'User does not exist. Please check your username.')
            
            return render(request, 'accounts/staff_login.html')
    
    return render(request, 'accounts/staff_login.html')


def login_p(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")  # Debug: Print credentials

        user = authenticate(request, username=username, password=password)
        print(f"Authenticated User: {user}")  # Debug: Print the authenticated user

        if user is not None:
            if user.role == 'patient':  # Compare with the string 'patient'
                login(request, user)
                print("Login successful, redirecting to p_dash")  # Debug: Print success message
                return redirect('p_det')
            else:
                print("User is not a patient")  # Debug: Print role mismatch
                return render(request, 'accounts/login_p.html', {'error': 'You are not a patient.'})
        else:
            print("Invalid credentials")  # Debug: Print authentication failure
            return render(request, 'accounts/login_p.html', {'error': 'Invalid credentials.'})
    return render(request, 'accounts/login_p.html')





@login_required
def staff_dash(request):
    try:
        # Fetch the StaffD record for the current user
        staff = StaffD.objects.get(user=request.user)
        full_name = staff.full_name
        staff_data = {
            'full_name': staff.full_name,
            'email': staff.email,
            'mobile_number': staff.mobile_number,
            'department': staff.department,
            'specialization': staff.specialization,
            'qualification': staff.qualification,
            'years_of_experience': staff.years_of_experience,
        }

        # Fetch the working hours for the staff member
        working_hours = WorkingHour.objects.filter(staff=staff)

        # Count the number of appointments for the staff member
        appointment_count = Appointment.objects.filter(doctor=staff).count()

        # Count the number of unique patients associated with the staff member
        patient_count = (
            Appointment.objects
            .filter(doctor=staff)  # Filter appointments by the doctor
            .values('patient')     # Group by patient
            .annotate(count=Count('patient'))  # Count unique patients
            .count()  # Get the total number of unique patients
        )
    except StaffD.DoesNotExist:
        full_name = "User"  # Default value if no StaffD record exists
        staff_data = None
        working_hours = None
        appointment_count = 0
        patient_count = 0

    # Pass the full_name, staff_data, working_hours, and counts to the template
    context = {
        'full_name': full_name,
        'staff_data': staff_data,
        'working_hours': working_hours,
        'appointment_count': appointment_count,
        'patient_count': patient_count,
    }
    return render(request, 'accounts/staff_dash.html', context)


@login_required
def staff_app(request):
    # Fetch the logged-in user
    user = request.user

    # Try to fetch the full name from the StaffD model (for doctors)
    try:
        staff = StaffD.objects.get(user=user)
        full_name = staff.full_name
    except StaffD.DoesNotExist:
        # If not a doctor, try to fetch the full name from the NurseReg model (for nurses)
        try:
            nurse = NurseReg.objects.get(user=user)
            full_name = nurse.full_name
        except NurseReg.DoesNotExist:
            # If neither exists, fall back to the user's username
            full_name = user.username

    # Fetch all appointments for the current doctor
    current_time = timezone.now()
    upcoming_appointments = Appointment.objects.filter(
        doctor=staff,  # Assuming the logged-in user is a doctor
        date__gte=current_time.date(),  # Upcoming or today's appointments
    ).order_by('date', 'start_time')

    old_appointments = Appointment.objects.filter(
        doctor=staff,  # Assuming the logged-in user is a doctor
        date__lt=current_time.date(),  # Past appointments
    ).order_by('-date', '-start_time')

    # Pass the data to the template
    context = {
        'full_name': full_name,
        'upcoming_appointments': upcoming_appointments,
        'old_appointments': old_appointments,
    }
    return render(request, 'accounts/staff_app.html', context)



@login_required
def staff_pat(request):
    # Fetch the logged-in user
    user = request.user

    # Initialize variables
    full_name = user.username
    appointments = []

    # Try to fetch the full name from the StaffD model (for doctors)
    if user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=user)
            full_name = staff.full_name
            # Fetch appointments for the current doctor
            appointments = Appointment.objects.filter(doctor=staff)
        except StaffD.DoesNotExist:
            pass

    # If not a doctor, try to fetch the full name from the NurseReg model (for nurses)
    elif user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=user)
            full_name = nurse.full_name
            # Fetch appointments for the current nurse
            appointments = Appointment.objects.filter(patient__patient_profile__isnull=False)  # Assuming nurses can see all patient appointments
        except NurseReg.DoesNotExist:
            pass

    # Extract unique patients and their relevant appointment details
    patients_data = {}
    for appointment in appointments:
        patient_user = appointment.patient
        try:
            patient = PatientReg.objects.get(user=patient_user)
            if patient.id not in patients_data:
                patients_data[patient.id] = {
                    'id': patient.id,  # Include the patient ID
                    'name': patient.full_name,
                    'contact': patient.mobile_number,
                    'last_appointment_date': appointment.date,
                    'upcoming_appointment_date': None,  # Initialize as None
                    'email': patient.email,  # Initialize as None
                }
            else:
                # Update the last appointment date if this appointment is more recent
                if appointment.date > patients_data[patient.id]['last_appointment_date']:
                    patients_data[patient.id]['last_appointment_date'] = appointment.date
        except PatientReg.DoesNotExist:
            continue

    # Check for upcoming appointments
    for appointment in appointments:
        if appointment.date > timezone.now().date():  # Check if the appointment is in the future
            patient_user = appointment.patient
            try:
                patient = PatientReg.objects.get(user=patient_user)
                if patient.id in patients_data:
                    patients_data[patient.id]['upcoming_appointment_date'] = appointment.date
            except PatientReg.DoesNotExist:
                continue

    # Convert the dictionary to a list for easier templating
    patients_list = list(patients_data.values())

    # Pass the full_name and patients_list to the template
    context = {
        'full_name': full_name,
        'patients_list': patients_list,
    }
    return render(request, 'accounts/staff_pat.html', context)

@login_required
def staff_pat1(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Fetch the logged-in user (doctor)
    user = request.user
    # department = None

    # Check if the user is a doctor from the Dialysis department
    is_dialysis_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_dialysis_doctor = staff.department == 'Dialysis'
            is_eyecare_doctor = staff.department == 'EyeCare'
            is_cardio_doctor = staff.department == 'Cardiology'
            
            
        except StaffD.DoesNotExist:
            pass
        
    # Pass the patient details and department-specific data to the template
    context = {
        'patient': patient,
        # 'department': department,
        'is_dialysis_doctor': is_dialysis_doctor,
        'is_eyecare_doctor': is_eyecare_doctor,
        "is_cardio_doctor": is_cardio_doctor,
    }
    return render(request, 'accounts/staff_pat1.html', context)



@login_required
def staff_pat_eyecare(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Fetch the logged-in user (doctor)
    user = request.user
    
    # Check if the user is a doctor from the EyeCare department
    is_eyecare_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_eyecare_doctor = staff.department == 'EyeCare'
        except StaffD.DoesNotExist:
            pass
    
    # Get all eye exams for this patient, ordered by most recent first
    eye_exams = EyeExam.objects.filter(patient=patient.user).order_by('-exam_date').values(
    'exam_date',
    'right_sph',
    'right_cyl',
    'right_axis',
    'right_prism',
    'left_sph',
    'left_cyl',
    'left_axis',
    'left_prism'
)
    
    # Pass the patient details and eye exam data to the template
    context = {
        'patient': patient,
        'is_eyecare_doctor': is_eyecare_doctor,
        'eye_exams': eye_exams,
        'full_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'accounts/staff_pat_eyecare.html', context)




@login_required
def staff_pat_dialysis(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Check if the user is a doctor and from the Dialysis department
    is_dialysis_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_dialysis_doctor = staff.department == 'Dialysis'
            is_eyecare_doctor = staff.department == 'EyeCare'
            is_cardio_doctor = staff.department == 'Cardiology'
        
            
        except StaffD.DoesNotExist:
            pass

    # If not a dialysis doctor, return a 403 Forbidden response
    if not is_dialysis_doctor:
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Fetch dialysis-related data
    weight_data = WeightTracking.objects.filter(patient=patient.user).order_by('date')
    
    # Fetch dialysis tubing data for the current month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    tubing_data = DialysisTubing.objects.filter(patient=patient.user, date__date__range=[start_of_month, end_of_month])
    
    # Fetch and aggregate water intake data by date
    water_intake_data = WaterIntake.objects.filter(patient=patient.user) \
        .values('date__date') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('-date__date')
    
    # Calculate today's total for the chart
    today_total = WaterIntake.objects.filter(
        patient=patient.user,
        date__date=timezone.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    
    context = {
        'patient': patient,
        'weight_data': weight_data,
        'tubing_data': tubing_data,
        'water_intake_data': water_intake_data,
        'today_total': today_total,
        'is_dialysis_doctor': is_dialysis_doctor,  # Pass this to template
        'is_eyecare_doctor': is_eyecare_doctor,
        "is_cardio_doctor": is_cardio_doctor,
    }
    return render(request, 'accounts/staff_pat_dialysis.html', context)


@login_required
def staff_pat_cardio(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Check if the user is a doctor and from the Cardiology department
    is_cardio_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_cardio_doctor = staff.department == 'Cardiology'
        except StaffD.DoesNotExist:
            pass

    # If not a cardiology doctor, return a 403 Forbidden response
    if not is_cardio_doctor:
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get all readings for the patient
    bp_records = BloodPressureReading.objects.filter(patient=patient.user).order_by('-record_date')
    cholesterol_records = CholesterolReading.objects.filter(patient=patient.user).order_by('-record_date')
    latest_cholesterol = cholesterol_records.first() if cholesterol_records.exists() else None
    ecg_records = ECGReading.objects.filter(patient=patient.user).order_by('-record_date')
    
    context = {
        'patient': patient,
        'bp_records': bp_records,
        'cholesterol_records': cholesterol_records,
        'latest_cholesterol': latest_cholesterol,
        'ecg_records': ecg_records,
        'is_cardio_doctor': is_cardio_doctor,
        'full_name': request.user.get_full_name(),
    }
    return render(request, 'accounts/staff_pat_cardio.html', context)


@login_required
def staff_pat_pres(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Only get prescriptions created by the current doctor for this patient
    prescriptions = Prescription.objects.filter(
        patient=patient.user,
        doctor=request.user
    ).order_by('-prescribed_at')
    
    # Department checks (keep your existing logic)
    is_dialysis_doctor = False
    is_eyecare_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_dialysis_doctor = staff.department == 'Dialysis'
            is_eyecare_doctor = staff.department == 'EyeCare'
            is_cardio_doctor = staff.department == 'Cardiology'
        
            
        except StaffD.DoesNotExist:
            pass

    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'is_dialysis_doctor': is_dialysis_doctor,
        'is_eyecare_doctor': is_eyecare_doctor,
        'full_name': request.user.get_full_name() or request.user.username,
        "is_cardio_doctor": is_cardio_doctor,
    }
    return render(request, 'accounts/staff_pat_pres.html', context)



@login_required
def add_prescription(request, patient_id):
    if request.method == 'POST':
        patient = get_object_or_404(PatientReg, id=patient_id)
        medicine_name = request.POST.get('medicine_name')
        dosage = request.POST.get('dosage')
        timing = request.POST.get('timing')
        before_after_food = request.POST.get('before_after_food')

        Prescription.objects.create(
            patient=patient.user,
            doctor=request.user,
            medicine_name=medicine_name,
            dosage=dosage,
            timing=timing,
            before_after_food=before_after_food
        )
        return redirect('staff_pat_pres', patient_id=patient_id)

    return redirect('staff_pat_pres', patient_id=patient_id)


@login_required
def staff_pat_rep(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    reports = PatientReport.objects.filter(patient=patient.user).order_by('-uploaded_at')
    comments = DoctorComment.objects.filter(patient=patient.user).order_by('-commented_at')
    
    # Check if the user is a doctor from the Dialysis department
    is_dialysis_doctor = False
    if request.user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=request.user)
            is_dialysis_doctor = staff.department == 'Dialysis'
            is_eyecare_doctor = staff.department == 'EyeCare'
            is_cardio_doctor = staff.department == 'Cardiology'
       
            
        except StaffD.DoesNotExist:
            pass
    
    context = {
        'patient': patient,
        'reports': reports,
        'comments': comments,
        'is_dialysis_doctor': is_dialysis_doctor,
        'is_eyecare_doctor': is_eyecare_doctor,
        "is_cardio_doctor": is_cardio_doctor,
    }
    return render(request, 'accounts/staff_pat_rep.html', context)


@login_required
def add_comment(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    if request.method == 'POST':
        form = DoctorCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.patient = patient.user
            comment.doctor = request.user
            comment.save()
            return redirect('staff_pat_rep', patient_id=patient.id)
    return redirect('staff_pat_rep', patient_id=patient.id)


@login_required
def staff_reg(request):
    if request.method == 'POST':
        # Extract form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        department = request.POST.get('department')
        sub_department = request.POST.get('sub_department')
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification')
        yrofexp = request.POST.get('yrofexp')
        whs = request.POST.get('whs')
        whe = request.POST.get('whe')

        # Check if a StaffD entry already exists for the user
        try:
            staff = StaffD.objects.get(user=request.user)
            # Update existing StaffD entry
            staff.full_name = full_name
            staff.email = email
            staff.mobile_number = mobile_number
            staff.gender = gender
            staff.age = age
            staff.department = department
            staff.sub_department = sub_department
            staff.specialization = specialization
            staff.qualification = qualification
            staff.years_of_experience = yrofexp
            staff.save()

            # Update working hours (delete existing and create new)
            WorkingHour.objects.filter(staff=staff).delete()  # Delete existing working hours
            WorkingHour.objects.create(
                staff=staff,
                start_time=whs,
                end_time=whe
            )

            messages.success(request, 'Staff details updated successfully!')
            return redirect('staff_dash')

        except StaffD.DoesNotExist:
            # Create new StaffD entry
            try:
                staff = StaffD.objects.create(
                    user=request.user,  # Associate with the logged-in user
                    full_name=full_name,
                    email=email,
                    mobile_number=mobile_number,
                    gender=gender,
                    age=age,
                    department=department,
                    sub_department=sub_department,
                    specialization=specialization,
                    qualification=qualification,
                    years_of_experience=yrofexp
                )
                
                # Save working hours
                WorkingHour.objects.create(
                    staff=staff,
                    start_time=whs,
                    end_time=whe
                )

                messages.success(request, 'Staff registration successful!')
                return redirect('staff_dash')

            except Exception as e:
                messages.error(request, f"Error: {e}")
                return redirect('staff_reg')

    return render(request, 'accounts/staff_reg.html')





@login_required
def nurse_dash(request):
    try:
        # Fetch the NurseReg record for the current user
        nurse = NurseReg.objects.get(user=request.user)
        full_name = nurse.full_name
        nurse_data = {
            'full_name': nurse.full_name,
            'mobile_number': nurse.mobile_number,
            'email': nurse.email,
            'gender': nurse.gender,
            'age': nurse.age,
            'department': nurse.department,
            'qualification': nurse.qualification,
            'blood_group': nurse.blood_group,
        }
    except NurseReg.DoesNotExist:
        full_name = "User"  # Default value if no NurseReg record exists
        nurse_data = None

    # Pass the full_name and nurse_data to the template
    context = {
        'full_name': full_name,
        'nurse_data': nurse_data,
    }
    return render(request, 'accounts/nurse_dash.html', context)



@login_required
def nurse_pat(request):
    # Fetch the logged-in nurse's details
    try:
        nurse = NurseReg.objects.get(user=request.user)
        full_name = nurse.full_name
        
        # Get doctors in the same department and sub-department
        doctors = StaffD.objects.filter(
            department=nurse.department,
            sub_department=nurse.sub_department
        )
        
        # Get appointments for these doctors
        appointments = Appointment.objects.filter(doctor__in=doctors)
        
        # Extract unique patients and their relevant appointment details
        patients_data = {}
        for appointment in appointments:
            patient_user = appointment.patient
            try:
                patient = PatientReg.objects.get(user=patient_user)
                if patient.id not in patients_data:
                    patients_data[patient.id] = {
                        'id': patient.id,
                        'name': patient.full_name,
                        'contact': patient.mobile_number,
                        'last_appointment_date': appointment.date,
                        'upcoming_appointment_date': None,
                        'email': patient.email,
                    }
                else:
                    # Update the last appointment date if this appointment is more recent
                    if appointment.date > patients_data[patient.id]['last_appointment_date']:
                        patients_data[patient.id]['last_appointment_date'] = appointment.date
            except PatientReg.DoesNotExist:
                continue

        # Check for upcoming appointments
        for appointment in appointments:
            if appointment.date > timezone.now().date():  # Future appointment
                patient_user = appointment.patient
                try:
                    patient = PatientReg.objects.get(user=patient_user)
                    if patient.id in patients_data:
                        patients_data[patient.id]['upcoming_appointment_date'] = appointment.date
                except PatientReg.DoesNotExist:
                    continue

        patients_list = list(patients_data.values())
        
    except NurseReg.DoesNotExist:
        full_name = "User"
        patients_list = []

    context = {
        'full_name': full_name,
        'patients_list': patients_list,
    }
    return render(request, 'accounts/nurse_pat.html', context)




@login_required
def nurse_pat1(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Fetch the nurse's details
    try:
        nurse = NurseReg.objects.get(user=request.user)
        nurse_data = {
            'department': nurse.department,
            'sub_department': nurse.sub_department
        }
        full_name = nurse.full_name
    except NurseReg.DoesNotExist:
        nurse_data = {}
        full_name = "User"

    context = {
        'patient': patient,
        'nurse_data': nurse_data,
        'full_name': full_name,
    }
    return render(request, 'accounts/nurse_pat1.html', context)



@login_required
def nurse_pat_dialysis(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Check if the user is a nurse and from the Dialysis department
    is_dialysis_nurse = False
    is_eyecare_nurse = False
    is_cardio_nurse = False
    
    if request.user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=request.user)
            is_dialysis_nurse = nurse.department == 'Dialysis'
            is_eyecare_nurse = nurse.department == 'EyeCare'
            is_cardio_nurse = nurse.department == 'Cardiology'
        except NurseReg.DoesNotExist:
            pass

    # If not a dialysis nurse, return a 403 Forbidden response
    if not is_dialysis_nurse:
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Fetch dialysis-related data
    weight_data = WeightTracking.objects.filter(patient=patient.user).order_by('date')
    
    # Fetch dialysis tubing data for the current month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    # tubing_data = DialysisTubing.objects.filter(patient=patient.user, date__date__range=[start_of_month, end_of_month])
    
    # Fetch and aggregate water intake data by date
    water_intake_data = WaterIntake.objects.filter(patient=patient.user) \
        .values('date__date') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('-date__date')
        
    tubing_data = DialysisTubing.objects.filter(patient=patient.user) \
        .annotate(week=TruncWeek('date')) \
        .values('week') \
        .annotate(total_count=Sum('tubing_count')) \
        .order_by('-week')
    
    # Calculate today's total for the chart
    today_total = WaterIntake.objects.filter(
        patient=patient.user,
        date__date=timezone.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'patient': patient,
        'weight_data': weight_data,
        'tubing_data': tubing_data,
        'water_intake_data': water_intake_data,
        'today_total': today_total,
        'is_dialysis_nurse': is_dialysis_nurse,
        'is_eyecare_nurse': is_eyecare_nurse,
        'is_cardio_nurse': is_cardio_nurse,
        'full_name': request.user.get_full_name() or nurse.full_name if 'nurse' in locals() else '',
    }
    return render(request, 'accounts/nurse_pat_dialysis.html', context)




@login_required
@require_POST
def add_tubing(request):
    try:
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        tubing_count = data.get('tubing_count')
        
        if not tubing_count or not patient_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        patient = get_object_or_404(PatientReg, id=patient_id)
        patient_user = patient.user
        
        # Check if the current user is a dialysis nurse
        if not request.user.role == User.NURSE:
            return JsonResponse({'error': 'Only nurses can perform this action'}, status=403)
        
        try:
            nurse = request.user.nursereg
            if nurse.department != 'Dialysis':
                return JsonResponse({'error': 'Only dialysis nurses can perform this action'}, status=403)
        except NurseReg.DoesNotExist:
            return JsonResponse({'error': 'Nurse profile not found'}, status=403)
        
        # Get today's date
        today = timezone.now().date()
        
        # Calculate total tubing count for today
        today_total = DialysisTubing.objects.filter(
            patient=patient_user,
            date__date=today
        ).aggregate(total=Sum('tubing_count'))['total'] or 0
        
        # Check if adding would exceed the daily limit
        if int(today_total) + int(tubing_count) > 5:
            return JsonResponse({
                'error': f'Cannot add {tubing_count} tubing(s). Today\'s total would exceed the maximum of 5. Remaining today: {5 - today_total}'
            }, status=400)
        
        # Create new tubing entry
        tubing = DialysisTubing.objects.create(
            patient=patient_user,
            tubing_count=tubing_count,
            department='Dialysis'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tubing data added successfully',
            'data': {
                'id': tubing.id,
                'date': tubing.date.strftime('%Y-%m-%d'),
                'tubing_count': tubing.tubing_count
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
@require_POST
def delete_tubing(request):
    try:
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return JsonResponse({'error': 'Missing patient ID'}, status=400)
        
        # Verify the patient exists
        patient = get_object_or_404(PatientReg, id=patient_id)
        patient_user = patient.user
        
        # Check if the current user is a dialysis nurse
        if not request.user.role == User.NURSE:
            return JsonResponse({'error': 'Only nurses can perform this action'}, status=403)
        
        try:
            nurse = request.user.nursereg  # Changed from nurse_profile to nursereg
            if nurse.department != 'Dialysis':
                return JsonResponse({'error': 'Only dialysis nurses can perform this action'}, status=403)
        except NurseReg.DoesNotExist:
            return JsonResponse({'error': 'Nurse profile not found'}, status=403)
        
        # Get the most recent tubing entry for this patient
        last_tubing = DialysisTubing.objects.filter(patient=patient_user).order_by('-date').first()
        
        if not last_tubing:
            return JsonResponse({'error': 'No tubing entries found'}, status=404)
        
        # Delete the entry
        deleted_id = last_tubing.id
        last_tubing.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Tubing entry deleted successfully',
            'deleted_id': deleted_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    

def has_dialysis_nurse_permission(nurse_user, patient_user):
    """
    Check if the nurse has permission to manage dialysis data for this patient
    """
    try:
        # Check if the user is a dialysis nurse
        nurse = nurse_user.nurse_profile
        if nurse.department != 'Dialysis':
            return False
        
        # Additional permission checks can be added here if needed
        # For example, checking if the nurse is assigned to this patient
        
        return True
        
    except AttributeError:
        # User doesn't have a nurse profile
        return False



@login_required
def nurse_pat_eyecare(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Check if the user is a nurse from the EyeCare department
    is_eyecare_nurse = False
    if request.user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=request.user)
            is_eyecare_nurse = nurse.department == 'EyeCare'
        except NurseReg.DoesNotExist:
            pass
    
    # Get all eye exams for this patient, ordered by most recent first
    eye_exams = EyeExam.objects.filter(patient=patient.user).order_by('-exam_date').values(
        'exam_date',
        'right_sph',
        'right_cyl',
        'right_axis',
        'right_prism',
        'left_sph',
        'left_cyl',
        'left_axis',
        'left_prism'
    )
    
    # Pass the patient details and eye exam data to the template
    context = {
        'patient': patient,
        'is_eyecare_nurse': is_eyecare_nurse,
        'eye_exams': eye_exams,
        'full_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'accounts/nurse_pat_eyecare.html', context)


@login_required
def nurse_pat_cardio(request, patient_id):
    # Fetch the patient details based on the patient_id
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Check if the user is a nurse from the Cardiology department
    is_cardio_nurse = False
    if request.user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=request.user)
            is_cardio_nurse = nurse.department == 'Cardiology'
        except NurseReg.DoesNotExist:
            pass

    # If not a cardiology nurse, return a 403 Forbidden response
    if not is_cardio_nurse:
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get all readings for the patient
    bp_records = BloodPressureReading.objects.filter(patient=patient.user).order_by('-record_date')
    cholesterol_records = CholesterolReading.objects.filter(patient=patient.user).order_by('-record_date')
    latest_cholesterol = cholesterol_records.first() if cholesterol_records.exists() else None
    ecg_records = ECGReading.objects.filter(patient=patient.user).order_by('-record_date')
    
    context = {
        'patient': patient,
        'bp_records': bp_records,
        'cholesterol_records': cholesterol_records,
        'latest_cholesterol': latest_cholesterol,
        'ecg_records': ecg_records,
        'is_cardio_nurse': is_cardio_nurse,
        'full_name': request.user.get_full_name(),
    }
    return render(request, 'accounts/nurse_pat_cardio.html', context)


@login_required
def nurse_pat_pres(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Get all prescriptions for this patient
    prescriptions = Prescription.objects.filter(
        patient=patient.user
    ).order_by('-prescribed_at')
    
    # Department checks for nurse
    is_dialysis_nurse = False
    is_eyecare_nurse = False
    is_cardio_nurse = False
    
    if request.user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=request.user)
            is_dialysis_nurse = nurse.department == 'Dialysis'
            is_eyecare_nurse = nurse.department == 'EyeCare'
            is_cardio_nurse = nurse.department == 'Cardiology'
            
            # Filter prescriptions to only show those from doctors in the same department
            if nurse.department:
                prescriptions = prescriptions.filter(
                    doctor__staff_profile__department=nurse.department,
                    doctor__staff_profile__sub_department=nurse.sub_department
                ).select_related('doctor__staff_profile')
        except NurseReg.DoesNotExist:
            pass

    # Group prescriptions by date and doctor
    grouped_prescriptions = {}
    for prescription in prescriptions:
        date_key = prescription.prescribed_at.strftime('%Y-%m-%d')
        
        # Get doctor's name safely
        doctor_name = "Unknown Doctor"
        if hasattr(prescription.doctor, 'staff_profile') and prescription.doctor.staff_profile:
            doctor_name = prescription.doctor.staff_profile.full_name or prescription.doctor.get_full_name()
        else:
            doctor_name = prescription.doctor.get_full_name()
        
        if date_key not in grouped_prescriptions:
            grouped_prescriptions[date_key] = {}
            
        if doctor_name not in grouped_prescriptions[date_key]:
            grouped_prescriptions[date_key][doctor_name] = []
            
        grouped_prescriptions[date_key][doctor_name].append(prescription)

    context = {
        'patient': patient,
        'grouped_prescriptions': grouped_prescriptions,
        'is_dialysis_nurse': is_dialysis_nurse,
        'is_eyecare_nurse': is_eyecare_nurse,
        'is_cardio_nurse': is_cardio_nurse,
        'full_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'accounts/nurse_pat_pres.html', context)


@login_required
def nurse_pat_rep(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    
    # Get reports uploaded by the patient
    reports = PatientReport.objects.filter(patient=patient.user).order_by('-uploaded_at')
    
    # Department checks for nurse
    is_dialysis_nurse = False
    is_eyecare_nurse = False
    is_cardio_nurse = False
    
    if request.user.role == User.NURSE:
        try:
            nurse = NurseReg.objects.get(user=request.user)
            is_dialysis_nurse = nurse.department == 'Dialysis'
            is_eyecare_nurse = nurse.department == 'EyeCare'
            is_cardio_nurse = nurse.department == 'Cardiology'
            
            # Filter comments to only show those from doctors in the same department/sub-department
            comments = DoctorComment.objects.filter(
                patient=patient.user,
                doctor__staff_profile__department=nurse.department,
                doctor__staff_profile__sub_department=nurse.sub_department
            ).order_by('-commented_at')
        except NurseReg.DoesNotExist:
            comments = DoctorComment.objects.none()
    
    context = {
        'patient': patient,
        'reports': reports,
        'comments': comments,
        'is_dialysis_nurse': is_dialysis_nurse,
        'is_eyecare_nurse': is_eyecare_nurse,
        'is_cardio_nurse': is_cardio_nurse,
        'full_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'accounts/nurse_pat_rep.html', context)



@login_required
def nurse_app(request):
    try:
        nurse = NurseReg.objects.get(user=request.user)
        full_name = nurse.full_name
        nurse_data = {
            'department': nurse.department,
            'sub_department': nurse.sub_department
        }
        
        doctors = StaffD.objects.filter(
            department=nurse.department,
            sub_department=nurse.sub_department
        )
        
        today = timezone.now().date()
        
        # Corrected select_related with proper related_name
        upcoming_appointments = Appointment.objects.filter(
            doctor__in=doctors,
            date__gte=today
        ).select_related(
            'patient__patient_profile',  # Using the correct related_name
            'doctor'
        ).order_by('date', 'start_time')
        
        old_appointments = Appointment.objects.filter(
            doctor__in=doctors,
            date__lt=today
        ).select_related(
            'patient__patient_profile',  # Using the correct related_name
            'doctor'
        ).order_by('-date', '-start_time')
        
    except NurseReg.DoesNotExist:
        full_name = "User"
        nurse_data = {}
        upcoming_appointments = []
        old_appointments = []

    context = {
        'full_name': full_name,
        'nurse_data': nurse_data,
        'upcoming_appointments': upcoming_appointments,
        'old_appointments': old_appointments,
    }
    return render(request, 'accounts/nurse_app.html', context)


@login_required
def nurse_reg(request):
    if request.method == 'POST':
        # Extract form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        department = request.POST.get('department')
        sub_department = request.POST.get('sub_department')  # New field
        qualification = request.POST.get('qualification')
        blood_group = request.POST.get('blood_group')
        
        # Check if a Nurse entry already exists for the user
        try:
            nurse = NurseReg.objects.get(user=request.user)
            # Update existing Nurse entry
            nurse.full_name = full_name
            nurse.email = email 
            nurse.mobile_number = mobile_number
            nurse.gender = gender
            nurse.age = age
            nurse.department = department
            nurse.sub_department = sub_department  # New field
            nurse.qualification = qualification
            nurse.blood_group = blood_group
            nurse.save()

            messages.success(request, 'Nurse details updated successfully!')
            return redirect('nurse_dash')

        except NurseReg.DoesNotExist:
            # Create new Nurse entry
            try:
                nurse = NurseReg.objects.create(
                    user=request.user,
                    full_name=full_name,
                    email=email, 
                    mobile_number=mobile_number,
                    gender=gender,
                    age=age,
                    department=department,
                    sub_department=sub_department,  # New field
                    qualification=qualification,
                    blood_group=blood_group
                )
                                
                messages.success(request, 'Nurse registration successful!')
                return redirect('nurse_dash')

            except Exception as e:
                messages.error(request, f"Error: {e}")
                return redirect('nurse_reg')

    return render(request, 'accounts/nurse_reg.html')


# Add this at the top of your views.py
DEPARTMENT_STRUCTURE = {
    "Cardiology": [
        "Heart Failure Clinic",
        "Electrophysiology (EP)",
        "Interventional Cardiology",
        "Preventive Cardiology",
        "Vascular Medicine"
    ],
    "EyeCare": [
        "Retina Services",
        "Glaucoma Services",
        "Cataract Services",
        "General Ophthalmology",
        "Optometry"
    ],
    "Dialysis": [
        "Nephrology",
        "Hemodialysis Unit",
        "Peritoneal Dialysis",
        "Interventional Radiology",
        "Nutrition"
    ],
    # Add other departments as needed
}

def admin_dash(request):
    # Query the database to get counts
    total_doctors = StaffD.objects.count()
    total_patients = PatientReg.objects.count()
    total_nurse = NurseReg.objects.count()
    total_appointment = Appointment.objects.count()
    patients = PatientReg.objects.all().select_related('user')
    
    # Get all departments from our predefined structure
    departments = sorted(DEPARTMENT_STRUCTURE.keys())
    
    # Get actual sub-departments that have data
    sub_departments_with_data = {}
    doctors = StaffD.objects.all()
    for doctor in doctors:
        if doctor.department and doctor.department in DEPARTMENT_STRUCTURE:
            if doctor.department not in sub_departments_with_data:
                sub_departments_with_data[doctor.department] = set()
            if doctor.sub_department:
                sub_departments_with_data[doctor.department].add(doctor.sub_department)
    
    # Convert sets to sorted lists
    for dept in sub_departments_with_data:
        sub_departments_with_data[dept] = sorted(sub_departments_with_data[dept])
    
    # Pass the counts and departments to the template
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_nurse': total_nurse,
        'total_appointment': total_appointment,
        'departments': departments,
        'sub_departments_json': json.dumps(DEPARTMENT_STRUCTURE),  # Send the full structure
        'patients': patients,
    }
    return render(request, 'accounts/admin_dash.html', context)



def get_department_data(request):
    department = request.GET.get('department', '')
    sub_department = request.GET.get('sub_department', '')
    
    if not department:
        return JsonResponse({'error': 'Department is required'}, status=400)
    
    try:
        # Get doctors in the selected department and sub-department
        doctors_query = StaffD.objects.filter(department=department)
        if sub_department and sub_department != "all":
            doctors_query = doctors_query.filter(sub_department=sub_department)
        
        doctors = list(doctors_query.values('id', 'full_name'))
        
        # Get appointments for these doctors
        appointments = Appointment.objects.filter(
            doctor_id__in=[doc['id'] for doc in doctors]
        ).select_related('patient').order_by('-date')
        
        # Get unique counts
        unique_doctors = len({doc['id'] for doc in doctors})
        unique_patients = len({app.patient_id for app in appointments})
        total_appointments = appointments.count()
        
        # Prepare response data
        data = []
        for appointment in appointments:
            doctor = next((doc for doc in doctors if doc['id'] == appointment.doctor_id), None)
            
            # Get patient name from related PatientReg if exists, otherwise use username
            patient_name = "Unknown"
            if hasattr(appointment.patient, 'patient_profile'):
                patient_name = appointment.patient.patient_profile.full_name
            elif hasattr(appointment.patient, 'get_full_name'):
                patient_name = appointment.patient.get_full_name()
            elif hasattr(appointment.patient, 'username'):
                patient_name = appointment.patient.username
            
            data.append({
                'doctor_name': doctor['full_name'] if doctor else 'Unknown',
                'patient_name': patient_name,
                'appointment_date': appointment.date.strftime('%Y-%m-%d') if appointment.date else '',
                'start_time': appointment.start_time.strftime('%H:%M') if appointment.start_time else '',
                'end_time': appointment.end_time.strftime('%H:%M') if appointment.end_time else '',
                'description': appointment.description,
            })
        
        return JsonResponse({
            'data': data,
            'counts': {
                'doctors': unique_doctors,
                'patients': unique_patients,
                'appointments': total_appointments
            }
        }, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    
def get_patient_metrics(request):
    patient_id = request.GET.get('patient_id')
    metric_type = request.GET.get('metric_type', '')
    time_range = request.GET.get('time_range', 'all')
    
    if not patient_id:
        return JsonResponse({'error': 'Patient ID is required'}, status=400)
    
    try:
        patient = User.objects.get(id=patient_id)
        now = timezone.now()
        date_filter = None
        
        # Set date filter based on time range
        if time_range == 'today':
            date_filter = now - timedelta(days=1)
        elif time_range == 'week':
            date_filter = now - timedelta(weeks=1)
        elif time_range == 'month':
            date_filter = now - timedelta(days=30)
        
        data = []
        counts = {
            'blood_pressure': 0,
            'cholesterol': 0,
            'weight': 0,
            'ecg': 0,
            'eye_exam': 0
        }
        
        # Blood Pressure
        if not metric_type or metric_type == 'blood_pressure':
            query = BloodPressureReading.objects.filter(patient=patient)
            if date_filter:
                query = query.filter(record_date__gte=date_filter)
            bp_readings = query.order_by('-record_date')
            
            counts['blood_pressure'] = bp_readings.count()
            for reading in bp_readings:
                data.append({
                    'metric_type': 'Blood Pressure',
                    'date': reading.record_date.strftime('%Y-%m-%d %H:%M'),
                    'measurements': f"{reading.systolic}/{reading.diastolic} mmHg (Pulse: {reading.pulse})",
                    'status': reading.status,
                })
        
        # Cholesterol
        if not metric_type or metric_type == 'cholesterol':
            query = CholesterolReading.objects.filter(patient=patient)
            if date_filter:
                query = query.filter(record_date__gte=date_filter)
            cholesterol_readings = query.order_by('-record_date')
            
            counts['cholesterol'] = cholesterol_readings.count()
            for reading in cholesterol_readings:
                data.append({
                    'metric_type': 'Cholesterol',
                    'date': reading.record_date.strftime('%Y-%m-%d %H:%M'),
                    'measurements': f"Total: {reading.total} | LDL: {reading.ldl} | HDL: {reading.hdl}",
                    'status': reading.status,
                })
        
        # Weight
        if not metric_type or metric_type == 'weight':
            query = WeightTracking.objects.filter(patient=patient)
            if date_filter:
                query = query.filter(date__gte=date_filter.date())
            weight_readings = query.order_by('-date')
            
            counts['weight'] = weight_readings.count()
            for reading in weight_readings:
                status = 'Normal' if 50 <= reading.weight <= 100 else 'Abnormal'
                data.append({
                    'metric_type': 'Weight',
                    'date': reading.date.strftime('%Y-%m-%d'),
                    'measurements': f"{reading.weight} kg",
                    'status': status,
                })
        
        # ECG
        if not metric_type or metric_type == 'ecg':
            query = ECGReading.objects.filter(patient=patient)
            if date_filter:
                query = query.filter(record_date__gte=date_filter)
            ecg_readings = query.order_by('-record_date')
            
            counts['ecg'] = ecg_readings.count()
            for reading in ecg_readings:
                data.append({
                    'metric_type': 'ECG',
                    'date': reading.record_date.strftime('%Y-%m-%d %H:%M'),
                    'measurements': f"HR: {reading.heart_rate}bpm ({reading.rhythm})",
                    'status': reading.health_status[1],
                })
        
        # Eye Exams
        if not metric_type or metric_type == 'eye_exam':
            query = EyeExam.objects.filter(patient=patient)
            if date_filter:
                query = query.filter(exam_date__gte=date_filter.date())
            eye_exams = query.order_by('-exam_date')
            
            counts['eye_exam'] = eye_exams.count()
            for exam in eye_exams:
                data.append({
                    'metric_type': 'Eye Exam',
                    'date': exam.exam_date.strftime('%Y-%m-%d'),
                    'measurements': f"Right: {exam.right_sph}/{exam.right_cyl} | Left: {exam.left_sph}/{exam.left_cyl}",
                    'status': 'Exam Completed',
                })
        
        return JsonResponse({
            'data': data,
            'counts': counts
        }, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

from django.http import JsonResponse

def get_schedule(request):
    doctor_name = request.GET.get('name')
    try:
        doctor = StaffD.objects.get(full_name=doctor_name)
        working_hours = WorkingHour.objects.filter(staff=doctor)

        if not working_hours.exists():
            return JsonResponse({'status': 'error', 'message': 'No working hours found for this doctor.'})

        # Combine working hours into a string
        hours = [
            f"{hour.start_time.strftime('%I:%M %p')} to {hour.end_time.strftime('%I:%M %p')}" 
            for hour in working_hours
        ]
        schedule = {
            'name': doctor.full_name,
            'working_hours': ', '.join(hours)
        }
        return JsonResponse({'status': 'success', 'schedule': schedule})
    except StaffD.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Doctor not found'})



from django.db.models import Q

def create_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        doctor_name = request.POST.get('doctor')
        patient_id = request.user.id  # Assuming the user is authenticated
        date = request.POST.get('date')
        start_time = request.POST.get('time')
        description = request.POST.get('description')

        try:
            # Convert start_time to time object and calculate end_time
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time = (datetime.combine(datetime.today(), start_time_obj) + timedelta(minutes=15)).time()

            # Fetch doctor instance
            doctor = StaffD.objects.get(full_name=doctor_name)

            # Check for overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time_obj,
            )
            if overlapping_appointments.exists():
                # Suggest the next available time slot
                existing_appointments = Appointment.objects.filter(
                    doctor=doctor,
                    date=date
                ).order_by('start_time')

                # Find a gap between appointments
                for i in range(len(existing_appointments) - 1):
                    current_end = existing_appointments[i].end_time
                    next_start = existing_appointments[i + 1].start_time

                    # Check if there's at least a 15-minute gap
                    if (datetime.combine(datetime.today(), next_start) - datetime.combine(datetime.today(), current_end)).seconds >= 15 * 60:
                        suggested_start = current_end
                        suggested_end = (datetime.combine(datetime.today(), suggested_start) + timedelta(minutes=15)).time()
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Appointment conflicts with an existing one.',
                            'suggested_time': f'{suggested_start.strftime("%H:%M")} - {suggested_end.strftime("%H:%M")}'
                        })

                # If no gaps, suggest a time after the last appointment
                if existing_appointments.exists():
                    last_end = existing_appointments.last().end_time
                    suggested_start = last_end
                    suggested_end = (datetime.combine(datetime.today(), suggested_start) + timedelta(minutes=15)).time()
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Appointment conflicts with an existing one.',
                        'suggested_time': f'{suggested_start.strftime("%H:%M")} - {suggested_end.strftime("%H:%M")}'
                    })

                # If no appointments exist
                return JsonResponse({
                    'status': 'error',
                    'message': 'Appointment conflicts with an existing one, but no suggestions are available.'
                })

            # Create new appointment
            Appointment.objects.create(
                doctor=doctor,
                patient_id=patient_id,
                date=date,
                start_time=start_time_obj,
                end_time=end_time,
                description=description,
            )
            return JsonResponse({'status': 'success', 'message': 'Appointment created successfully.'})

        except StaffD.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Doctor not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)




def get_doctors_by_department(request):
    department = request.GET.get('department', '')
    if not department:
        return JsonResponse({'status': 'error', 'message': 'Department parameter is required'}, status=400)
    
    try:
        doctors = StaffD.objects.filter(department=department).values('id', 'full_name')
        return JsonResponse({
            'status': 'success',
            'doctors': list(doctors)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_doctor_details(request):
    doctor_id = request.GET.get('id', '')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Doctor ID is required'}, status=400)
    
    try:
        doctor = StaffD.objects.get(id=doctor_id)
        working_hours = WorkingHour.objects.filter(staff=doctor).values( 'start_time', 'end_time')
        
        return JsonResponse({
            'status': 'success',
            'specialization': doctor.specialization,
            'qualification': doctor.qualification,
            # 'experience': f"{doctor.years_of_experience} years",
            'working_hours': list(working_hours)
        })
    except StaffD.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Doctor not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
        
        

@login_required
def p_dash(request):
    current_time = timezone.now()
    
    # Get unique departments from StaffD model
    departments = StaffD.objects.values_list('department', flat=True).distinct()
    
    upcoming_appointments = Appointment.objects.filter(
        Q(patient=request.user, date__gt=current_time.date()) |
        Q(patient=request.user, date=current_time.date(), start_time__gt=current_time.time())
    ).order_by('date', 'start_time')

    old_appointments = Appointment.objects.filter(
        Q(patient=request.user, date__lt=current_time.date()) |
        Q(patient=request.user, date=current_time.date(), end_time__lte=current_time.time())
    ).order_by('-date', '-start_time')

    context = {
        'upcoming_appointments': upcoming_appointments,
        'old_appointments': old_appointments,
        'departments': departments,
    }
    return render(request, 'accounts/p_dash.html', context)


@login_required
def p_pres(request):
    # Debug: Print the current user
    print(f"Fetching prescriptions for user: {request.user}")

    # Fetch prescriptions for the current patient and group them by the date they were prescribed
    prescriptions = Prescription.objects.filter(patient=request.user).annotate(
        prescribed_date=TruncDate('prescribed_at')
    ).order_by('-prescribed_at')

    # Debug: Print the number of prescriptions found
    # print(f"Found {prescriptions.count()} prescriptions for {request.user}")

    # Group prescriptions by date and then by doctor
    grouped_prescriptions = {}
    for prescription in prescriptions:
        date_key = prescription.prescribed_date.strftime('%Y-%m-%d')
        
        # Access the doctor's full name from the StaffD model
        doctor_name = prescription.doctor.staff_profile.full_name  # Access via the related_name 'staff_profile'

        # Debug: Print the doctor's name
        # print(f"Processing prescription for doctor: {doctor_name} on {date_key}")

        # Create the date group if it doesn't exist
        if date_key not in grouped_prescriptions:
            grouped_prescriptions[date_key] = {}

        # Create the doctor group if it doesn't exist
        if doctor_name not in grouped_prescriptions[date_key]:
            grouped_prescriptions[date_key][doctor_name] = []

        # Add the prescription to the corresponding date and doctor group
        grouped_prescriptions[date_key][doctor_name].append(prescription)

    context = {
        'grouped_prescriptions': grouped_prescriptions,
    }
    return render(request, 'accounts/p_pres.html', context)




@login_required
def send_reminders(request, date):
    if request.method == 'POST':
        try:
            # Fetch prescriptions for the given date
            prescriptions = Prescription.objects.filter(
                patient=request.user,
                prescribed_at__date=date
            )

            # Update the `reminders_set` field for all prescriptions
            prescriptions.update(reminders_set=True)

            # Send initial email
            patient_email = request.user.patient_profile.email
            subject = 'Medication Reminders Added'
            message = f'You have added reminders for your medicines prescribed on {date}.'
            html_message = f'''
            <html>
                <body>
                    <p>You have added reminders for your medicines prescribed on <strong>{date}</strong>.</p>
                    <p>Here are your prescribed medicines and their dosages:</p>
                    <ul>
                        {"".join([f"<li>{prescription.medicine_name} - {prescription.dosage}</li>" for prescription in prescriptions])}
                    </ul>
                    <p>Thank you for using MediCare.</p>
                </body>
            </html>
            '''
            email = EmailMessage(
                subject,
                message,
                f'MediCare <{settings.EMAIL_HOST_USER}>',
                [patient_email],
                reply_to=[settings.EMAIL_HOST_USER],
            )
            email.content_subtype = 'html'
            email.body = html_message
            email.send(fail_silently=False)

            # Add success message
            messages.success(request, f'Reminders set for {date}. Initial email sent to {patient_email}.')

            return JsonResponse({'success': True})
        except Exception as e:
            # Debug: Print the error
            print(f"Error: {e}")

            # Add error message
            messages.error(request, f'Failed to send reminders. Error: {e}')

            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Debug: Print invalid request method
        print("Invalid request method")

        # Add error message
        messages.error(request, 'Invalid request method')

        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    
    
    
@login_required
def prescription_list(request):
    # Group prescriptions by date and doctor
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-prescribed_at')
    
    # Group by date
    grouped_prescriptions = {}
    for prescription in prescriptions:
        date_str = prescription.prescribed_at.strftime('%Y-%m-%d')
        doctor_name = prescription.doctor.staff_profile.full_name
        
        if date_str not in grouped_prescriptions:
            grouped_prescriptions[date_str] = {}
        
        if doctor_name not in grouped_prescriptions[date_str]:
            grouped_prescriptions[date_str][doctor_name] = []
            
        grouped_prescriptions[date_str][doctor_name].append(prescription)
    
    context = {
        'grouped_prescriptions': grouped_prescriptions,
    }
    return render(request, 'accounts/p_pres.html', context)




@login_required
@require_POST
def toggle_reminders(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, patient=request.user)
    
    # Toggle the enabled status
    prescription.reminders_enabled = not prescription.reminders_enabled
    prescription.save()
    
    if prescription.reminders_enabled:
        # Create reminders based on doctor's timing pattern
        times = prescription.get_reminder_times()
        for time_str in times:
            hour, minute = map(int, time_str.split(':'))
            
            # Create or get schedule
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )
            
            # Create or update periodic task
            task_name = f'prescription_{prescription.id}_reminder_{time_str.replace(":", "")}'
            PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    'crontab': schedule,
                    'task': 'accounts.tasks.send_medication_reminder',
                    'args': json.dumps([prescription.id]),
                    'enabled': True,
                }
            )
    else:
        # Disable all reminders for this prescription
        PeriodicTask.objects.filter(
            name__startswith=f'prescription_{prescription.id}_reminder_'
        ).delete()
    
    return JsonResponse({
        'success': True,
        'enabled': prescription.reminders_enabled,
        'timing_pattern': prescription.timing_pattern,
        'reminder_times': prescription.get_reminder_times() if prescription.reminders_enabled else []
    })
    
    
    

@login_required
def p_rep(request):
    # Handle file uploads
    if request.method == 'POST' and 'file_submit' in request.POST:
        form = PatientReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = request.user
            report.file_name = request.FILES['file'].name
            report.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('p_rep')
        else:
            messages.error(request, 'Invalid file Format (.pdf,.doc,.jpg,.png). Please try again.')

    # Handle doctor's comments
    if request.method == 'POST' and 'comment_submit' in request.POST:
        comment_form = DoctorCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.patient = request.user
            comment.doctor = request.user  # Assuming the doctor is the logged-in user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('p_rep')
        else:
            messages.error(request, 'Invalid comment. Please try again.')

    # Fetch doctor's comments for the current patient
    doctor_comments = DoctorComment.objects.filter(patient=request.user).order_by('-commented_at')

    # Fetch uploaded files for the current patient
    uploaded_files = PatientReport.objects.filter(patient=request.user)

    # Initialize forms
    form = PatientReportForm()
    comment_form = DoctorCommentForm()

    context = {
        'doctor_comments': doctor_comments,
        'uploaded_files': uploaded_files,
        'form': form,
        'comment_form': comment_form,
    }
    return render(request, 'accounts/p_rep.html', context)



@login_required
def delete_report(request, report_id):
    report = get_object_or_404(PatientReport, id=report_id, patient=request.user)
    report.delete()
    return redirect('p_rep')

@login_required
def p_det(request):
    # Fetch the PatientReg data for the current user
    try:
        patient = PatientReg.objects.get(user=request.user)
    except PatientReg.DoesNotExist:
        patient = None  # Handle the case where the patient profile doesn't exist

    context = {
        'patient': patient,
    }
    return render(request, 'accounts/p_det.html', context)




@login_required
def p_reg(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            # Check if a PatientReg entry already exists for the user
            try:
                patient = PatientReg.objects.get(user=request.user)
                # Update existing PatientReg entry
                patient.full_name = form.cleaned_data['full_name']
                patient.date_of_birth = form.cleaned_data['date_of_birth']
                patient.email = form.cleaned_data['email']
                patient.mobile_number = form.cleaned_data['mobile_number']
                patient.gender = form.cleaned_data['gender']
                patient.age = form.cleaned_data['age']
                patient.blood_group = form.cleaned_data['blood_group']
                patient.marital_status = form.cleaned_data['marital_status']
                patient.address = form.cleaned_data['address']
                patient.emergency_contact_name = form.cleaned_data['emergency_contact_name']
                patient.emergency_contact_number = form.cleaned_data['emergency_contact_number']
                patient.occupation = form.cleaned_data['occupation']
                patient.habits = form.cleaned_data['habits']
                patient.medical_history = form.cleaned_data['medical_history']
                patient.disease = form.cleaned_data['disease']
                patient.save()

                messages.success(request, 'Patient details updated successfully!')
                return redirect('p_dash')  # Redirect to patient dashboard

            except PatientReg.DoesNotExist:
                # Create new PatientReg entry
                patient = form.save(commit=False)
                patient.user = request.user
                patient.save()

                messages.success(request, 'Patient registration successful!')
                return redirect('p_dash')  # Redirect to patient dashboard

        else:
            # If the form is invalid, display errors
            print(form.errors)
            messages.error(request, 'Invalid form data. Please correct the errors below.')
            return render(request, 'accounts/p_reg.html', {'form': form})

    else:
        # If the request method is GET, check if the patient already exists
        try:
            patient = PatientReg.objects.get(user=request.user)
            # Pre-fill the form with existing data
            form = PatientForm(instance=patient)
        except PatientReg.DoesNotExist:
            # If no patient exists, create a new form
            form = PatientForm()

    return render(request, 'accounts/p_reg.html', {'form': form})



@login_required
def p_dialysis(request):
    # Get weekly tubing data for the template
    tubing_data = DialysisTubing.objects.filter(patient=request.user) \
        .annotate(week=TruncWeek('date')) \
        .values('week') \
        .annotate(total_count=Sum('tubing_count')) \
        .order_by('-week')[:8]
    
    context = {
        'tubing_data': tubing_data,
    }
    return render(request, 'accounts/p_dialysis.html', context)




@csrf_exempt
@login_required
def fetch_weight_data(request, patient_id=None):
    if request.method == 'GET':
        # For nurses accessing patient data
        if patient_id:
            patient = get_object_or_404(PatientReg, id=patient_id)
            user = patient.user
        # For patients accessing their own data
        else:
            user = request.user
            
        weights = WeightTracking.objects.filter(patient=user).order_by('date')
        data = [{
            'date': entry.date.strftime('%Y-%m-%d'),
            'weight': float(entry.weight)
        } for entry in weights]
        return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
@login_required
def add_weight(request, patient_id=None):
    try:
        data = json.loads(request.body)
        weight = data.get('weight')
        
        if not weight:
            return JsonResponse({'error': 'Weight is required'}, status=400)
        
        # For nurses accessing patient data
        if patient_id:
            patient = get_object_or_404(PatientReg, id=patient_id)
            user = patient.user
            
            # Verify nurse has permission
            if not request.user.role == User.NURSE:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        # For patients accessing their own data
        else:
            user = request.user
        
        WeightTracking.objects.create(
            patient=user,
            weight=weight,
            date=timezone.now()
        )
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
@login_required
def delete_weight(request, patient_id=None):
    try:
        # For nurses accessing patient data
        if patient_id:
            patient = get_object_or_404(PatientReg, id=patient_id)
            user = patient.user
            
            # Verify nurse has permission
            if not request.user.role == User.NURSE:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        # For patients accessing their own data
        else:
            user = request.user
            
        last_entry = WeightTracking.objects.filter(patient=user).order_by('-date').first()
        if last_entry:
            last_entry.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'error': 'No entries found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def fetch_water_intake(request):
    if request.method == 'GET':
        today = timezone.now().date()
        # Get today's total
        today_total = WaterIntake.objects.filter(
            patient=request.user, 
            date__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        return JsonResponse({'today_total': today_total})
    
@csrf_exempt
@login_required
def fetch_water_history(request):
    if request.method == 'GET':
        # Get daily totals
        water_data = WaterIntake.objects.filter(patient=request.user) \
            .values('date__date') \
            .annotate(total_amount=Sum('amount')) \
            .order_by('-date__date')
        
        history = [{
            'date': entry['date__date'].strftime('%Y-%m-%d'),
            'amount': entry['total_amount']
        } for entry in water_data]
        
        return JsonResponse(history, safe=False)

@csrf_exempt
@login_required
def add_water_intake(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        if amount:
            WaterIntake.objects.create(
                patient=request.user,
                amount=amount,
                date=timezone.now()
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def delete_water_intake(request):
    if request.method == 'POST':
        last_entry = WaterIntake.objects.filter(patient=request.user).order_by('-date').first()
        if last_entry:
            last_entry.delete()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def fetch_tubing_data(request):
    if request.method == 'GET':
        # Get tubing data grouped by week
        tubing_data = DialysisTubing.objects.filter(patient=request.user) \
            .annotate(week=TruncWeek('date')) \
            .values('week') \
            .annotate(total_count=Sum('tubing_count')) \
            .order_by('-week')[:8]  # Get last 8 weeks of data
        
        # Format the data for the chart
        data = [{
            'week': entry['week'].strftime('%Y-%m-%d'),
            'count': entry['total_count']
        } for entry in tubing_data]
        
        return JsonResponse(data, safe=False)


@login_required
def p_cardio(request):
    if request.method == 'POST':
        try:
            systolic = int(request.POST.get('systolic'))
            diastolic = int(request.POST.get('diastolic'))
            pulse = int(request.POST.get('pulse'))
            
            # Determine blood pressure status
            if systolic < 90 and diastolic < 60:
                status = 'Hypotension'
            elif systolic < 120 and diastolic < 80:
                status = 'Normal'
            elif 120 <= systolic <= 129 and diastolic < 80:
                status = 'Elevated'
            elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
                status = 'Hypertension Stage 1'
            elif systolic >= 140 or diastolic >= 90:
                status = 'Hypertension Stage 2'
            else:
                status = 'Unclassified'
                          
            # Create and save the reading with status
            BloodPressureReading.objects.create(
                patient=request.user,
                systolic=systolic,
                diastolic=diastolic,
                pulse=pulse,
                status=status
            )
            messages.success(request, 'Blood pressure reading saved successfully!')
            return redirect('p_cardio')
            
        except ValueError as e:
            messages.error(request, 'Please enter valid numbers for all fields')
        except Exception as e:
            messages.error(request, 'An error occurred while saving your reading')

    # Get all readings for the current user
    bp_records = BloodPressureReading.objects.filter(patient=request.user).order_by('-record_date')
    # Add cholesterol data to context
    cholesterol_records = CholesterolReading.objects.filter(patient=request.user).order_by('-record_date')
    latest_cholesterol = cholesterol_records.first() if cholesterol_records.exists() else None
    
    ecg_records = ECGReading.objects.filter(patient=request.user).order_by('-record_date')
    
    
    # Prepare data for the chart (all readings, reversed for chronological order)
    chart_data = {
        'dates': [record.record_date.strftime('%Y-%m-%d %H:%M') for record in bp_records[::-1]],
        'systolic': [record.systolic for record in bp_records[::-1]],
        'diastolic': [record.diastolic for record in bp_records[::-1]],
        'pulse': [record.pulse for record in bp_records[::-1]],
    }
    
    return render(request, 'accounts/p_cardio.html', {
        'bp_records': bp_records,
        'chart_data': chart_data,
        'cholesterol_records': cholesterol_records,
        'latest_cholesterol': latest_cholesterol,
        'ecg_records': ecg_records,
        
    })
    
    
from django.template.defaulttags import register

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None
    
    
@login_required
def p_cholesterol(request):
    if request.method == 'POST':
        try:
            total = int(request.POST.get('total'))
            ldl = int(request.POST.get('ldl'))
            hdl = int(request.POST.get('hdl'))
            triglycerides = int(request.POST.get('triglycerides'))
            
            # Determine cholesterol status
            if total < 200 and ldl < 100 and hdl >= 60 and triglycerides < 150:
                status = 'Optimal'
            elif (200 <= total <= 239) or (100 <= ldl <= 159) or (150 <= triglycerides <= 199):
                status = 'Borderline High'
            elif total >= 240 or ldl >= 160 or triglycerides >= 200:
                status = 'High'
            elif hdl < 40:
                status = 'Low HDL Risk'
            else:
                status = 'Unclassified'
                          
            # Create and save the reading with status
            CholesterolReading.objects.create(
                patient=request.user,
                total=total,
                ldl=ldl,
                hdl=hdl,
                triglycerides=triglycerides,
                status=status
            )
            messages.success(request, 'Cholesterol reading saved successfully!')
            return redirect('p_cardio')  # Redirect back to cardio page
            
        except ValueError as e:
            messages.error(request, 'Please enter valid numbers for all fields')
        except Exception as e:
            messages.error(request, 'An error occurred while saving your reading')

    # Always redirect back to p_cardio even for GET requests
    return redirect('p_cardio')



@login_required
def p_ecg(request):
    if request.method == 'POST':
        try:
            ECGReading.objects.create(
                patient=request.user,
                heart_rate=int(request.POST.get('heart_rate')),
                pr_interval=int(request.POST.get('pr_interval')),
                qrs_duration=int(request.POST.get('qrs_duration')),
                qt_interval=int(request.POST.get('qt_interval')),
                qtc=int(request.POST.get('qtc'))
            )
            messages.success(request, 'ECG reading saved successfully!')
        except Exception as e:
            messages.error(request, f'Error saving ECG reading: {str(e)}')
        return redirect('p_cardio')
    
    return redirect('p_cardio')



@login_required
def p_eyecare(request):
    if request.method == 'POST':
        form = EyeExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.patient = request.user
            exam.department = 'Eyecare'
            exam.save()
            messages.success(request, 'Eye exam data saved successfully!')
            return redirect('p_eyecare')
    else:
        form = EyeExamForm()
    
    eye_exams = EyeExam.objects.filter(patient=request.user).order_by('-exam_date')
    
    context = {
        'eye_exams': eye_exams,
        'form': form,
    }
    return render(request, 'accounts/p_eyecare.html', context)



def ad_app(request):
    current_time = timezone.now()

    # Upcoming appointments: date and start_time are in the future
    upcoming_appointments = Appointment.objects.filter(
        date__gt=current_time.date()
    ).exclude(
        date=current_time.date(), start_time__lte=current_time.time()
    ).order_by('date', 'start_time')

    # Old appointments: date and start_time are in the past or equal to the current time
    old_appointments = Appointment.objects.filter(
        date__lt=current_time.date()
    ).exclude(
        date=current_time.date(), start_time__gt=current_time.time()
    ).order_by('-date', '-start_time')

    context = {
        'upcoming_appointments': upcoming_appointments,
        'old_appointments': old_appointments,
    }
    return render(request, 'accounts/ad_app.html', context)



@login_required
def ad_pat(request):
    patients = PatientReg.objects.select_related('user').all()
    context = {
        'patients': patients,
    }
    return render(request, 'accounts/ad_pat.html', context)



@login_required
def edit_patient(request, patient_id):
    print("Current user:", request.user)  # Debugging
    patient = get_object_or_404(PatientReg, id=patient_id)
    if request.method == 'POST':
        print("Updating patient:", patient.full_name)  # Debugging
        print("Form data:", request.POST)  # Debugging

        # Update all fields of the PatientReg model
        patient.full_name = request.POST.get('full_name')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.email = request.POST.get('email')
        patient.mobile_number = request.POST.get('mobile_number')
        patient.gender = request.POST.get('gender')
        patient.age = request.POST.get('age')
        patient.blood_group = request.POST.get('blood_group')
        patient.marital_status = request.POST.get('marital_status')
        patient.address = request.POST.get('address')
        patient.emergency_contact_name = request.POST.get('emergency_contact_name')
        patient.emergency_contact_number = request.POST.get('emergency_contact_number')
        patient.occupation = request.POST.get('occupation')
        patient.habits = request.POST.get('habits')
        patient.medical_history = request.POST.get('medical_history')
        patient.disease = request.POST.get('disease')
        patient.save()

        # Reset password if provided
        new_password = request.POST.get('new_password')
        if new_password:
            user = patient.user
            user.password = make_password(new_password)
            user.save()

        messages.success(request, 'Patient details updated successfully.')
        return redirect('ad_pat')
    return redirect('ad_pat')


def delete_patient(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    if request.method == 'POST':
        user = patient.user
        patient.delete()
        user.delete()
        messages.success(request, 'Patient and associated user deleted successfully.')
        return redirect('ad_pat')
    return redirect('ad_pat')


def add_patient(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = 'patient'  # Default role

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('ad_pat')

        # Create a new User with the role 'patient'
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        # Create a new PatientReg entry with default values
        PatientReg.objects.create(
            user=user,
            full_name='-',  # Default value
            date_of_birth=timezone.now().date(),  # Set a default date (e.g., today's date)
            email=None,  # Default value
            mobile_number='-',  # Default value
            gender='-',  # Default value
            age=0,  # Default value
            blood_group='-',  # Default value
            marital_status='-',  # Default value
            address='-',  # Default value
            emergency_contact_name='-',  # Default value
            emergency_contact_number='-',  # Default value
            occupation='-',  # Default value
            habits='-',  # Default value
            medical_history='None',  # Default value
            disease='None',  # Default value
        )

        messages.success(request, 'Patient added successfully.')
        return redirect('ad_pat')

    return render(request, 'accounts/ad_pat.html')


def ad_nurse(request):
    # Fetch all nurses from the database
    nurses = NurseReg.objects.all()

    # Pass the nurses to the template
    context = {
        'nurses': nurses,
    }
    return render(request, 'accounts/ad_nurse.html', context)


def edit_nurse(request, nurse_id):
    nurse = get_object_or_404(NurseReg, id=nurse_id)

    if request.method == 'POST':
        # Update nurse details
        nurse.full_name = request.POST.get('full_name')
        nurse.mobile_number = request.POST.get('mobile_number')
        nurse.email = request.POST.get('email')
        nurse.gender = request.POST.get('gender')
        nurse.age = request.POST.get('age')
        nurse.department = request.POST.get('department')
        nurse.sub_department = request.POST.get('sub_department')  # New field
        nurse.qualification = request.POST.get('qualification')
        nurse.blood_group = request.POST.get('blood_group')
        nurse.save()

        # Reset password if provided
        new_password = request.POST.get('new_password')
        if new_password:
            user = nurse.user
            user.password = make_password(new_password)
            user.save()

        messages.success(request, 'Nurse details updated successfully.')
        return redirect('ad_nurse')

    return redirect('ad_nurse')



def add_nurse(request):
    if request.method == 'POST':
        # Extract form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = 'nurse'  # Default role

        # Create a new User with the role 'nurse'
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        # Create a new NurseReg entry with default values
        NurseReg.objects.create(
            user=user,
            full_name='-',  # Default value
            email=None,  # Set email to None (null)
            mobile_number='-',  # Default value
            gender='-',  # Default value
            age=0,  # Default value
            department='-',  # Default value
            qualification='-',  # Default value
            blood_group='-',  # Default value
        )

        messages.success(request, 'Nurse added successfully.')
        return redirect('ad_nurse')  # Redirect to the nurses list page

    return render(request, 'accounts/ad_nurse.html')


def delete_nurse(request, nurse_id):
    # Fetch the NurseReg entry
    nurse = get_object_or_404(NurseReg, id=nurse_id)
    
    if request.method == 'POST':
        # Fetch the associated User
        user = nurse.user
        
        # Delete the NurseReg entry
        nurse.delete()
        
        # Delete the User entry
        user.delete()
        
        messages.success(request, 'Nurse and associated user deleted successfully.')
        return redirect('ad_nurse')  # Redirect to the nurses list page
    
    return redirect('ad_nurse')



def ad_doc(request):
    # Fetch all doctors from the StaffD model and their related User data
    doctors = StaffD.objects.select_related('user').all()
    
    context = {
        'doctors': doctors,
    }
    return render(request, 'accounts/ad_doc.html', context)




# Edit Doctor Details
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(StaffD, id=doctor_id)
    if request.method == 'POST':
        # Update doctor details
        doctor.full_name = request.POST.get('full_name')
        doctor.email = request.POST.get('email')
        doctor.mobile_number = request.POST.get('mobile_number')
        doctor.department = request.POST.get('department')
        doctor.sub_department = request.POST.get('sub_department')  
        doctor.specialization = request.POST.get('specialization')
        doctor.qualification = request.POST.get('qualification')
        doctor.years_of_experience = request.POST.get('years_of_experience')
        doctor.save()

        # Reset password if provided
        new_password = request.POST.get('new_password')
        if new_password:
            user = doctor.user
            user.password = make_password(new_password)
            user.save()

        messages.success(request, 'Doctor details updated successfully.')
        return redirect('ad_doc')
    return redirect('ad_doc')

# # Reset Password
# def reset_password(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     if request.method == 'POST':
#         new_password = request.POST.get('new_password')
#         user.password = make_password(new_password)  # Hash the new password
#         user.save()
#         messages.success(request, 'Password reset successfully.')
#         return redirect('ad_doc')
#     return render(request, 'accounts/reset_password.html', {'user': user})



def delete_doctor(request, doctor_id):
    # Fetch the StaffD entry
    doctor = get_object_or_404(StaffD, id=doctor_id)
    
    if request.method == 'POST':
        # Fetch the associated User
        user = doctor.user
        
        # Delete the StaffD entry
        doctor.delete()
        
        # Delete the User entry
        user.delete()
        
        messages.success(request, 'Doctor and associated user deleted successfully.')
        return redirect('ad_doc')
    
    return redirect('ad_doc')



def add_doctor(request):
    if request.method == 'POST':
        # Extract form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = 'doctor'  # Default role

        # Create a new User with the role 'doctor'
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        # Create a new StaffD entry with default values
        StaffD.objects.create(
            user=user,
            full_name='-',  # Default value
            email=None,  # Default value
            mobile_number='-',  # Default value
            gender='-',  # Default value
            age=0,  # Default value
            department='-',  # Default value
            specialization='-',  # Default value
            qualification='-',  # Default value
            years_of_experience='-',  # Default value
            # whs='-',  # Default value
            # whe='-',  # Default value
        )

        return redirect('ad_doc')  # Redirect to the doctors list page

    return render(request, 'accounts/ad_doc.html')



from django.core.mail import EmailMessage

def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'accepted'
    appointment.save()

    # Fetch the patient's email from the PatientReg model
    try:
        patient_reg = appointment.patient.patient_profile  # Access the related PatientReg
        patient_email = patient_reg.email
    except PatientReg.DoesNotExist:
        messages.error(request, 'Patient profile not found. Notification not sent.')
        return redirect(reverse('staff_app'))

    # Check if the patient has an email
    if not patient_email:
        messages.error(request, 'Patient email is missing. Notification not sent.')
        return redirect(reverse('staff_app'))

    # Send email to patient
    subject = 'Appointment Accepted'
    message = f'Your appointment on {appointment.date} at {appointment.start_time} has been accepted.'
    html_message = f'''
    <html>
        <body>
            <p>Your appointment on <strong>{appointment.date}</strong> at <strong>{appointment.start_time}</strong> has been accepted.</p>
            <p>Thank you for choosing MediCare.</p>
        </body>
    </html>
    '''
    from_email = f'MediCare <{settings.EMAIL_HOST_USER}>'
    recipient_list = [patient_email]

    email = EmailMessage(
        subject,
        message,
        from_email,
        recipient_list,
        reply_to=[settings.EMAIL_HOST_USER],
    )
    email.content_subtype = 'html'  # Set content type to HTML
    email.body = html_message  # Add HTML content

    try:
        email.send(fail_silently=False)
        # Success message with recipient email
        messages.success(request, f'Appointment accepted and notification sent to {patient_email}.')
    except Exception as e:
        # Error message
        messages.error(request, f'Failed to send email to {patient_email}. Error: {e}')

    return redirect(reverse('staff_app'))



def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'rejected'
    appointment.save()

    # Fetch the patient's email from the PatientReg model
    try:
        patient_reg = appointment.patient.patient_profile  # Access the related PatientReg
        patient_email = patient_reg.email
    except PatientReg.DoesNotExist:
        messages.error(request, 'Patient profile not found. Notification not sent.')
        return redirect(reverse('staff_app'))

    # Check if the patient has an email
    if not patient_email:
        messages.error(request, 'Patient email is missing. Notification not sent.')
        return redirect(reverse('staff_app'))

    # Send email to patient
    subject = 'Appointment Rejected'
    message = f'Your appointment on {appointment.date} at {appointment.start_time} has been rejected.'
    html_message = f'''
    <html>
        <body>
            <p>Your appointment on <strong>{appointment.date}</strong> at <strong>{appointment.start_time}</strong> has been rejected.</p>
            <p>Please contact us for further assistance.</p>
        </body>
    </html>
    '''
    from_email = f'MediCare <{settings.EMAIL_HOST_USER}>'
    recipient_list = [patient_email]

    email = EmailMessage(
        subject,
        message,
        from_email,
        recipient_list,
        reply_to=[settings.EMAIL_HOST_USER],
    )
    email.content_subtype = 'html'  # Set content type to HTML
    email.body = html_message  # Add HTML content

    try:
        email.send(fail_silently=False)
        # Success message with recipient email
        messages.success(request, f'Appointment rejected and notification sent to {patient_email}.')
    except Exception as e:
        # Error message
        messages.error(request, f'Failed to send email to {patient_email}. Error: {e}')

    return redirect(reverse('staff_app'))

# def send_email(request):
#     email()
#     return redirect('/')


def ad_rep(request):
    return render(request, 'accounts/ad_rep.html')