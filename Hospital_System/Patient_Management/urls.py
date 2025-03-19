from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('online_consultations/', views.online, name='online_consultations'),
    path('physical_appointment/', views.physical, name='physical_appointment'),
    path('emergency_care/', views.emergency, name='emergency_care'),
    path('emergency_booked/<int:emergency_id>/',views.emergency_booked, name='emergency_booked'),
    path('booking-success/<int:appointment_id>/', views.booking, name='booking_success'),
    path('AI/',views.AI, name='AI'),
    path('online_doctor/',views.online_doctor, name='online_doctor'),
    path('blog',views.blog,name = 'blog'),
    path('about/',views.about, name='about'),
    path('types/', views.appointment_types, name='appointment_types'),
    path('times/<str:appointment_type>/', views.appointment_times, name='appointment_times'),
    path('book/<str:appointment_type>/<path:appointment_time>/', views.book_appointment, name='book_appointment'),
    path( 'patients/',views.patients, name='patients'),
    path('history/',views.history, name='history'),

]
 