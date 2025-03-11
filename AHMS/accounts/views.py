from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User,PatientReg,StaffD,WorkingHour,Appointment
from .forms import PatientForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def logoutp(request):
    logout(request)    
    return redirect('landing')

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
            # If authentication fails, display an error message
            return render(request, 'accounts/staff_login.html', {'error': 'Invalid credentials'})
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
                return redirect('p_dash')
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

def staff_dash(request):
    return render(request, 'accounts/staff_dash.html')

def staff_app(request):
    return render(request, 'accounts/staff_app.html')

def staff_pat(request):
    return render(request, 'accounts/staff_pat.html')

def staff_pat1(request):
    return render(request, 'accounts/staff_pat1.html')

@login_required
def staff_reg(request):
    if request.method == 'POST':
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

        # Validate and save staff information
        try:
            staff = StaffD.objects.create(
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



    
    
def nurse_dash(request):
    return render(request, 'accounts/nurse_dash.html')

def nurse_pat(request):
    return render(request, 'accounts/nurse_pat.html')

def nurse_pat1(request):
    return render(request, 'accounts/nurse_pat1.html')

def nurse_app(request):
    return render(request, 'accounts/nurse_app.html')

def admin_dash(request):
    # Query the database to get counts
    total_doctors = StaffD.objects.count()
    total_patients = PatientReg.objects.count()
    
    # Pass the counts to the template
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
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



def p_pres(request):
    return render(request, 'accounts/p_pres.html')

def p_rep(request):
    return render(request, 'accounts/p_rep.html')

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
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            return redirect('p_dash')  # Redirect to patient dashboard
        else:
            print(form.errors) 
            return render(request, 'accounts/p_reg.html', {'form': form, 'error': 'Invalid form data.'})
    else:
        form = PatientForm()
    return render(request, 'accounts/p_reg.html', {'form': form})

def ad_app(request):
    return render(request, 'accounts/ad_app.html')

def ad_pat(request):
    return render(request, 'accounts/ad_pat.html')


def ad_nurse(request):
    return render(request, 'accounts/ad_nurse.html')

def ad_doc(request):
    # Fetch all doctors from the StaffD model
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

# Delete Doctor
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(StaffD, id=doctor_id)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor deleted successfully.')
        return redirect('ad_doc')
    return redirect('ad_doc')