from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .models import DoctorProfile
from django.contrib.auth.decorators import login_required
from django .contrib.auth.models import User, auth
# Create your views here.
def register (request):
    return render(request, 'register.html')
 
def doctor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            # Check if the user is a doctor
            if DoctorProfile.objects.filter(user=user).exists():
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('doctor_dashboard')  # Redirect to doctor's dashboard
            else:
                messages.error(request, "You are not authorized to log in as a doctor.")
                return redirect('doctor_login')

        else:
            messages.error(request, "Invalid username or password!")
            return redirect('doctor_login')

    return render(request, 'doctor_login.html')
@login_required
def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')
def logout(request):
    auth.logout(request)
    return redirect ('doctor_login')


def sign_in(request) :
    if request.method == 'POST':
        first_name = request.POST['first_name']  
        last_name = request.POST['last_name']
        username = request.POST['username'] 
        password1 = request.POST['password1'] 
        password2 = request.POST['password2']  
        email = request.POST['email']

        if password1 != password2:
                messages.error(request,"Password dont match!")
                return redirect('signup')
        if User.objects.filter(email = email).exists():
                messages.error(request, "Email already registerd!")
                return redirect('signup')
        if User.objects.filter(username=username).exists():
                messages.error(request,"Username already taken,Choose another username")
                return redirect('signup')
        patient = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password1,
        )
        patient.save()
        messages.success(request, "Account Created Successfully!")
        return redirect('log_in')
    return render (request, 'signup.html')

def log_in(request):
     if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        patient = auth.authenticate(username=username,password=password)

        if patient is not None:
             auth.login(request, patient)
             messages.success(request,"Login Suiccessful!Welcome back.")
             return redirect('Patient_Dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('log_in')
     return render(request, 'login.html')
@login_required
def Patient_Dashboard(request):
     return render(request, 'Patient_Dashboard.html')