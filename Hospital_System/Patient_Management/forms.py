from django import forms
from .models import PhysicalAppointment
from .models import EmergencyCare,online_doctor
class PhysicalAppointmentForm(forms.ModelForm):
    class Meta:
        model = PhysicalAppointment
        fields = ['name', 'email', 'phone_no', 'service_needed', 'appointment_date']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
        }
class EmergencyCareForm(forms.ModelForm):
    class Meta:
        model = EmergencyCare
        fields = ['patient_name','contact_number','condition_description','priority_level','location']
        widgets = {
            'priority_level': forms.Select(choices=EmergencyCare.priority_level),
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class online_doctorForm(forms.ModelForm):
    class Meta:
        model = online_doctor
        fields = ['name', 'email', 'phone_number','service_type','date','time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }