from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User,PatientReg
from .forms import PatientForm

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


def login_p(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        print(f"Username: {username}, Password: {password}")  # Debug log
        
        if user and user.role == 'PATIENT':
            login(request, user)
            return redirect('p_dash')
        else:
            return render(request, 'accounts/login_p.html', {'error': 'Invalid credentials or not a patient.'})
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


def p_dash(request):
    return render(request, 'accounts/p_dash.html')

def p_pres(request):
    return render(request, 'accounts/p_pres.html')

def p_rep(request):
    return render(request, 'accounts/p_rep.html')

def p_det(request):
    return render(request, 'accounts/p_det.html')


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
    return render(request, 'accounts/ad_doc.html')