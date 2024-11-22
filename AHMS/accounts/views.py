from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import User

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
        # print("Form submitted")
        # print("Username:", username)


        if user is not None:
            if user.role == User.DOCTOR:
                login(request, user)
                return redirect('staff_dash')
            elif user.role == User.NURSE:
                login(request, user)
                return redirect('nurse_dash')
            elif user.role == User.ADMIN:
                login(request, user)
                return redirect('admin_dash')
        else:
            # If authentication fails, display an error message
            return render(request, 'accounts/staff_login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/staff_login.html')


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

def nurse_dash(request):
    return render(request, 'accounts/nurse_dash.html')

def nurse_pat(request):
    return render(request, 'accounts/nurse_pat.html')

def nurse_pat1(request):
    return render(request, 'accounts/nurse_pat1.html')

def nurse_app(request):
    return render(request, 'accounts/nurse_app.html')

def admin_dash(request):
    return render(request, 'accounts/admin_dash.html')