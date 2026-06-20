from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import DoctorProfile
from .models import Appointment

PASSWORD = "Str0ngPass!23"


def next_weekday_slot():
    d = datetime.now().date() + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return datetime.combine(d, time(10, 0))


class BookingTests(APITestCase):
    def test_physical_appointment_public_create(self):
        resp = self.client.post(
            reverse("physical-list"),
            {"name": "Sam", "email": "s@example.com", "phone_no": "0712",
             "service_needed": "Dentist", "appointment_date": "2030-01-01"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_physical_list_requires_staff(self):
        # Anonymous → 401; authenticated non-staff → 403.
        self.assertEqual(self.client.get(reverse("physical-list")).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(User.objects.create_user("plain", password=PASSWORD))
        self.assertEqual(self.client.get(reverse("physical-list")).status_code, status.HTTP_403_FORBIDDEN)

    def test_emergency_public_create(self):
        resp = self.client.post(
            reverse("emergency-list"),
            {"patient_name": "Sam", "contact_number": "0712",
             "condition_description": "fall", "priority_level": "High", "location": "ER"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class AppointmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("pat", email="p@example.com", password=PASSWORD)
        self.client.force_authenticate(self.user)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(reverse("appointment-list")).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_and_list_own(self):
        slot = next_weekday_slot().isoformat()
        resp = self.client.post(
            reverse("appointment-list"), {"appointment_type": "Dentist", "appointment_time": slot}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get(reverse("appointment-list")).data["count"], 1)

    def test_slots_excludes_booked(self):
        slot = next_weekday_slot()
        Appointment.objects.create(patient=self.user, appointment_type="Dentist", appointment_time=slot)
        resp = self.client.get(reverse("appointment-slots"), {"type": "Dentist"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(slot.isoformat(), resp.data["booked"])

    def test_types_from_doctor_specialties(self):
        DoctorProfile.objects.create(user=User.objects.create_user("dr", password=PASSWORD), specialty="Surgery")
        resp = self.client.get(reverse("appointment-types"))
        self.assertIn("Surgery", resp.data["types"])

    def test_for_doctor_without_profile_forbidden(self):
        resp = self.client.get(reverse("appointment-for-doctor"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ContactTests(APITestCase):
    def test_contact_public(self):
        resp = self.client.post(
            reverse("contact"),
            {"name": "Sam", "email": "s@example.com", "subject": "Hi", "message": "Hello"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
