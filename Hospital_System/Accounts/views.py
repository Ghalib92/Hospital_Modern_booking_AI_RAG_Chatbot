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