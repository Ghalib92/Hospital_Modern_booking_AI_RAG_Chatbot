from django.urls import path
from . import views



urlpatterns = [
    
     path('login/',views.doctor_login, name='doctor_login'),
     path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
     path('logout/', views.logout, name='logout'),
     path('log_in/', views.log_in, name='log_in'),
     path('signup/',views.sign_in, name='signup'),
     path('Dashboard/', views.Patient_Dashboard, name='Patient_Dashboard'),

    
]
