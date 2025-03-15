from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User,PatientReg,StaffD,WorkingHour,Appointment,NurseReg
from .forms import PatientForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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
    except StaffD.DoesNotExist:
        full_name = "User"  # Default value if no StaffD record exists
        staff_data = None
        working_hours = None

    # Pass the full_name, staff_data, and working_hours to the template
    context = {
        'full_name': full_name,
        'staff_data': staff_data,
        'working_hours': working_hours,
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

    # Pass the full_name to the template
    context = {
        'full_name': full_name,
    }
    return render(request, 'accounts/staff_app.html', context)


@login_required
def staff_pat(request):
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

    # Pass the full_name to the template
    context = {
        'full_name': full_name,
    }
    return render(request, 'accounts/staff_pat.html',context)



def staff_pat1(request):
    return render(request, 'accounts/staff_pat1.html')




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
            email='',  # Default value
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