from django.urls import path
from . import views



urlpatterns = [
    
    path('login/',views.doctor_login, name='doctor_login'),
     path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
     path('logout/', views.logout, name='logout'),

]
