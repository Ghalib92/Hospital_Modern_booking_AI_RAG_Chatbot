from django import forms
from .models import PhysicalAppointment
from .models import EmergencyCare,online_doctor
class PhysicalAppointmentForm(forms.ModelForm):
    class Meta:
        model = PhysicalAppointment
        fields = ['name', 'email', 'phone_no', 'service_needed', 'appointment_date']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
                   'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select appointment date', 'type': 'date'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here...', 'rows': 3}),
       
        }
class EmergencyCareForm(forms.ModelForm):
    class Meta:
        model = EmergencyCare
        fields = ['patient_name','contact_number','condition_description','priority_level','location']
        widgets = {
            'priority_level': forms.Select(choices=EmergencyCare.priority_level),
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter patient name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'condition_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the condition', 'rows': 3}),
            'priority_level': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
      
             
        }

        
class online_doctorForm(forms.ModelForm):
    class Meta:
        model = online_doctor
        fields = ['name', 'email', 'phone_number','service_type','date','time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }