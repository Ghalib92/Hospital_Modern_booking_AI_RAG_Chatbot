from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .forms import PhysicalAppointmentForm,online_doctorForm
from .models import PhysicalAppointment,Blog,Appointment
from .forms import EmergencyCareForm
from .models import EmergencyCare
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta, time
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())  
def online(request):
    template = loader.get_template('online_consultations.html')
    return HttpResponse(template.render())  
def physical(request):
    if request.method == 'POST':
        
        form = PhysicalAppointmentForm(request.POST)
        if form.is_valid():
           new_appointment= form.save()
           user_email = new_appointment.email  # Field from the model
           subject = 'Booking Confirmation'
           message = (
                f'Dear {new_appointment.name},\n\n'
                f'Your booking has been confirmed. Here are the details:\n\n'
                f'Service: {new_appointment.service_needed}\n'
                 f'Appointment.date: {new_appointment.appointment_date}\n'
                f'Thank you for choosing us!\n\n'
                f'Best regards,\n'
                f'Coast General Hospital'
            )
        from_email = settings.EMAIL_HOST_USER

            # Send the email
        try:
                send_mail(subject, message, from_email, [user_email])
        except Exception as e:
                return render(request, 'email_error.html', {'error': str(e)})

        return redirect('booking_success',appointment_id=new_appointment.id)  # Replace with your success page
    else:
        form = PhysicalAppointmentForm()

    return render(request, 'physical_appointment.html', {'form': form})
def booking(request,appointment_id):
    appointment = get_object_or_404(PhysicalAppointment, id=appointment_id)
    
    context = {
        'service':appointment.name,
        'appointment_date':appointment.appointment_date,
        'email': appointment.email

 }
    return render(request,'booking_success.html', context)
def emergency(request):
     if request.method == 'POST':
          form = EmergencyCareForm(request.POST)
          if form.is_valid():
             new_emergency = form.save()
                
          return redirect('emergency_booked',emergency_id=new_emergency.id)
           
     else:
        form = EmergencyCareForm()

    # If you forgot this line, the view returns None
     return render(request, 'emergency_care.html', {'form': form})
def emergency_booked(request,emergency_id):
     emergency = get_object_or_404(EmergencyCare, id=emergency_id)
     context = {
          'name':emergency.patient_name,
          'contact':emergency.contact_number
     }
     return render(request, 'emergency_booked.html',context)

def AI(request):
       template = loader.get_template('AI.html')
       return HttpResponse(template.render())  

def online_doctor(request):
     if request.method == 'POST':
          form = online_doctorForm(request.POST)
          if form.is_valid():
            new_online = form.save()
            return redirect('online_doctor',)
           
     else:
        form = online_doctorForm()
                
     return render(request, 'online_doctor.html',{'form': form})
          
     
def blog (request):
    blogs = Blog.objects.all()
    return render(request, 'blog.html', {'blogs': blogs})  # Pass blogs to the template
     

def about(request):
    return render (request , 'about.html')



@login_required
def appointment_types(request):
    return render(request, 'appointment_types.html')



@login_required
def appointment_times(request, appointment_type):
    today = datetime.now().date()
    available_times = []
    booked_times = []
    for i in range(5):  # Monday to Friday
        current_date = today + timedelta(days=i)
        if current_date.weekday() < 5:
            time_slots = [
                (8, 9), (10, 11), (12, 13), (14, 15), (16, 17)
            ]
            for start_hour, end_hour in time_slots:
                start_time = datetime.combine(current_date, time(start_hour, 0))
                if Appointment.objects.filter(appointment_time=start_time, appointment_type=appointment_type).exists():
                    booked_times.append(start_time)
                else:
                    available_times.append(start_time)
    return render(request, 'appointment_times_list.html', {
        'appointment_type': appointment_type,
        'available_times': available_times,
        'booked_times': booked_times
    })
@login_required
def book_appointment(request, appointment_type, appointment_time):
    # Convert appointment_time from string to datetime
    appointment_time = datetime.fromisoformat(appointment_time)

    # Create appointment with 'patient' instead of 'user'
    appointment = Appointment.objects.create(
        patient=request.user,  # FIX: Use 'patient' instead of 'user'
        appointment_type=appointment_type,
        appointment_time=appointment_time
    )

    # Send confirmation email
    send_mail(
         'Appointment Confirmation',
            f'''
            Dear {request.user.username},

            Your {appointment_type} appointment has been successfully scheduled for {appointment_time}. 

            Please ensure you arrive on time or join the online session as scheduled. If you need to reschedule or cancel, kindly do so in advance through your account.

            For any inquiries, feel free to contact our support team.

            Best regards,  
            Coast General Hospital.
   ''',
         settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False,
    )

    return HttpResponse("Appointment booked and confirmation email sent!")


def patients(request):
    return render(request, 'patients.html')

def history(request):
    return render(request, 'history.html')