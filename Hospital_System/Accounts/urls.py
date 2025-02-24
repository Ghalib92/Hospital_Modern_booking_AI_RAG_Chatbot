from django.urls import path
from . import views



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/',views.doctor_login, name='doctor_login'),
     path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

]
