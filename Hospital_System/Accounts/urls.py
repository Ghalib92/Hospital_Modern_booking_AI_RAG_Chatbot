from django.urls import path
from . import views

app_name = 'accounts'  # ✅ Define an app namespace

urlpatterns = [
    path('register/', views.register, name='register'),
]
