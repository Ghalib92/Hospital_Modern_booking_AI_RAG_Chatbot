from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DoctorProfile

PASSWORD = "Str0ngPass!23"


class AuthTests(APITestCase):
    def test_register_then_login(self):
        resp = self.client.post(
            reverse("register"),
            {"username": "pat", "email": "pat@example.com", "password": PASSWORD},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", resp.data)

        resp = self.client.post(reverse("login"), {"username": "pat", "password": PASSWORD})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_profile_requires_auth(self):
        self.assertEqual(self.client.get(reverse("profile")).status_code, status.HTTP_401_UNAUTHORIZED)


class DoctorDirectoryTests(APITestCase):
    def setUp(self):
        u = User.objects.create_user("drwho", password=PASSWORD)
        DoctorProfile.objects.create(user=u, specialty="Dentist")

    def test_doctor_list_public(self):
        resp = self.client.get(reverse("doctor-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_non_staff_cannot_create_doctor(self):
        user = User.objects.create_user("plain", password=PASSWORD)
        self.client.force_authenticate(user)
        resp = self.client.post(reverse("doctor-list"), {"specialty": "Surgery"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
