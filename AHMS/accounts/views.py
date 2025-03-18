from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User,PatientReg,StaffD,WorkingHour,Appointment,NurseReg,PatientReport,DoctorComment,Prescription,WeightTracking,WaterIntake,DialysisTubing
from .forms import PatientForm,PatientReportForm,DoctorCommentForm,WeightTrackingForm,WaterIntakeForm,DialysisTubingForm
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
from django.db.models import Count
from django.db.models.functions import TruncDate

from django.core.mail import send_mail
from django.urls import reverse

from .models import User 

def logoutp(request):
    logout(request)    
    return redirect('login_p')

def logouts(request):
    logout(request)    
    return redirect('staff_login')

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


def basestaff(request):
    return render(request, 'accounts/basestaff.html')

def landing(request):
    return render(request, 'accounts/landing.html')


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
    department = None

    # Check if the user is a doctor and fetch their department
    if user.role == User.DOCTOR:
        try:
            staff = StaffD.objects.get(user=user)
            department = staff.department
        except StaffD.DoesNotExist:
            pass

    # Initialize department-specific data
    weight_data = []
    tubing_data = []
    water_intake_data = []

    # Fetch dialysis-related data if the doctor belongs to the dialysis department
    if department == 'Dialysis':
        # Fetch weight tracking data
        weight_data = WeightTracking.objects.filter(patient=patient.user).order_by('date')
        
        # Fetch dialysis tubing data for the current month
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        tubing_data = DialysisTubing.objects.filter(patient=patient.user, date__date__range=[start_of_month, end_of_month])
        
        # Fetch water intake data for the current day
        water_intake_data = WaterIntake.objects.filter(patient=patient.user, date__date=today)

    # Debug: Print water intake data
    print("Water Intake Data:", water_intake_data)

    # Pass the patient details and department-specific data to the template
    context = {
        'patient': patient,
        'department': department,
        'weight_data': weight_data,
        'tubing_data': tubing_data,
        'water_intake_data': water_intake_data,
    }
    return render(request, 'accounts/staff_pat1.html', context)
@login_required
def staff_pat_pres(request, patient_id):
    patient = get_object_or_404(PatientReg, id=patient_id)
    prescriptions = Prescription.objects.filter(patient=patient.user).order_by('-prescribed_at')
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
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
    
    context = {
        'patient': patient,
        'reports': reports,
        'comments': comments,
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
    return render(request, 'accounts/nurse_pat.html',context)

def nurse_pat1(request):
    return render(request, 'accounts/nurse_pat1.html')

@login_required
def nurse_app(request):
    try:
        # Fetch the current nurse's department
        nurse = NurseReg.objects.get(user=request.user)
        department = nurse.department

        # Fetch all doctors in the same department
        doctors_in_department = StaffD.objects.filter(department=department)

        # Fetch upcoming appointments (date >= today)
        upcoming_appointments = Appointment.objects.filter(
            doctor__in=doctors_in_department,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')

        # Fetch old appointments (date < today)
        old_appointments = Appointment.objects.filter(
            doctor__in=doctors_in_department,
            date__lt=timezone.now().date()
        ).order_by('-date', '-start_time')

    except NurseReg.DoesNotExist:
        # If no nurse record exists, show no appointments
        upcoming_appointments = []
        old_appointments = []

    # Pass the data to the template
    context = {
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
        qualification = request.POST.get('qualification')
        blood_group = request.POST.get('blood_group')
        
        # Check if a Nurse entry already exists for the user
        try:
            nurse = NurseReg.objects.get(user=request.user)
            # Update existing Nurse entry
            nurse.full_name = full_name
            # nurse.email = email if email else None  # Set email to None if empty
            nurse.email = email 
            nurse.mobile_number = mobile_number
            nurse.gender = gender
            nurse.age = age
            nurse.department = department
            nurse.qualification = qualification
            nurse.blood_group = blood_group
            nurse.save()

            messages.success(request, 'Nurse details updated successfully!')
            return redirect('nurse_dash')  # Redirect to nurse dashboard or profile page

        except NurseReg.DoesNotExist:
            # Create new Nurse entry
            try:
                nurse = NurseReg.objects.create(
                    user=request.user,  # Associate with the logged-in user
                    full_name=full_name,
                    email=email, 
                    # email=email if email else None,  # Set email to None if empty
                    mobile_number=mobile_number,
                    gender=gender,
                    age=age,
                    department=department,
                    qualification=qualification,
                    blood_group=blood_group
                )
                                
                messages.success(request, 'Nurse registration successful!')
                return redirect('nurse_dash')  # Redirect to nurse dashboard or profile page

            except Exception as e:
                messages.error(request, f"Error: {e}")
                return redirect('nurse_reg')

    return render(request, 'accounts/nurse_reg.html')




def admin_dash(request):
    # Query the database to get counts
    total_doctors = StaffD.objects.count()
    total_patients = PatientReg.objects.count()
    total_nurse = NurseReg.objects.count()
    
    # Pass the counts to the template
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_nurse': total_nurse,
    }
    return render(request, 'accounts/admin_dash.html', context)




@login_required
def p_dash(request):
    current_time = timezone.now()

    # Fetch upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        Q(patient=request.user, date__gt=current_time.date()) |  # Future dates
        Q(patient=request.user, date=current_time.date(), start_time__gt=current_time.time())  # Today but future time
    ).order_by('date', 'start_time')

    # Fetch old appointments
    old_appointments = Appointment.objects.filter(
        Q(patient=request.user, date__lt=current_time.date()) |  # Past dates
        Q(patient=request.user, date=current_time.date(), end_time__lte=current_time.time())  # Today but time has elapsed
    ).order_by('-date', '-start_time')

    # Format time in 24-hour format for display
    for appointment in upcoming_appointments:
        appointment.start_time = appointment.start_time.strftime('%H:%M')
        appointment.end_time = appointment.end_time.strftime('%H:%M')

    for appointment in old_appointments:
        appointment.start_time = appointment.start_time.strftime('%H:%M')
        appointment.end_time = appointment.end_time.strftime('%H:%M')

    context = {
        'upcoming_appointments': upcoming_appointments,
        'old_appointments': old_appointments,
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
    return render(request, 'accounts/p_dialysis.html')




@csrf_exempt
@login_required
def fetch_weight_data(request):
    if request.method == 'GET':
        weights = WeightTracking.objects.filter(patient=request.user).order_by('date')
        data = [{
            'date': entry.date.strftime('%Y-%m-%d'),
            'weight': float(entry.weight)
        } for entry in weights]
        return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def add_weight(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        weight = data.get('weight')
        if weight:
            WeightTracking.objects.create(
                patient=request.user,
                weight=weight,
                date=timezone.now()
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def delete_weight(request):
    if request.method == 'POST':
        last_entry = WeightTracking.objects.filter(patient=request.user).order_by('-date').first()
        if last_entry:
            last_entry.delete()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
@login_required
def fetch_water_intake(request):
    if request.method == 'GET':
        today = timezone.now().date()
        water_entries = WaterIntake.objects.filter(patient=request.user, date__date=today)
        total_consumed = sum(entry.amount for entry in water_entries)
        return JsonResponse({'total_consumed': total_consumed})

@csrf_exempt
@login_required
def fetch_water_history(request):
    if request.method == 'GET':
        water_entries = WaterIntake.objects.filter(patient=request.user).order_by('-date')
        history = [{
            'date': entry.date.strftime('%Y-%m-%d'),
            'amount': entry.amount
        } for entry in water_entries]
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
def fetch_tubing_data(request):
    if request.method == 'GET':
        today = timezone.now().date()
        start_of_month = today.replace(day=1)  # Start of the current month
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # End of the current month

        # Fetch tubing entries for the current month
        tubing_entries = DialysisTubing.objects.filter(patient=request.user, date__date__range=[start_of_month, end_of_month])

        # Group tubing entries by week
        tubing_data = {}
        for entry in tubing_entries:
            week_number = (entry.date.date() - start_of_month).days // 7 + 1
            if week_number not in tubing_data:
                tubing_data[week_number] = 0
            tubing_data[week_number] += 1

        # Fill in missing weeks with 0
        data = [{'week': week, 'count': tubing_data.get(week, 0)} for week in range(1, 6)]  # Max 5 weeks in a month

        return JsonResponse(data, safe=False)



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
        # new_email = request.POST.get('email')

        # # Debugging: Print the new_email value
        # print(f"New Email: {new_email}")

        # # Skip duplicate email check if new_email is None or blank
        # if new_email is not None and new_email.strip() != "":  # Only check if new_email is not None and not empty
        #     print("Performing duplicate email check")
        #     if NurseReg.objects.filter(email=new_email).exclude(id=nurse_id).exists():
        #         messages.error(request, 'Email already exists. Please use a different email.')
        #         return redirect('ad_nurse')
        # else:
        #     print("Skipping duplicate email check (email is None or blank)")

        # Update nurse details
        nurse.full_name = request.POST.get('full_name')
        nurse.mobile_number = request.POST.get('mobile_number')
        nurse.email = request.POST.get('email')
        # nurse.email = new_email or None  # Set to None if empty
        nurse.gender = request.POST.get('gender')
        nurse.age = request.POST.get('age')
        nurse.department = request.POST.get('department')
        nurse.qualification = request.POST.get('qualification')
        nurse.blood_group = request.POST.get('blood_group')
        nurse.save()

        # Reset password if provided
        new_password = request.POST.get('new_password')
        if new_password: 
        # if new_password and new_password.strip():  # Check if new_password is not empty
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