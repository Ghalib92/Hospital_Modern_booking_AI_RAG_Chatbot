from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets

from .models import DoctorProfile
from .serializers import DoctorProfileSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Register a new patient account."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's account."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DoctorProfileViewSet(viewsets.ModelViewSet):
    """Doctor directory. Public to read; staff manage entries."""

    queryset = DoctorProfile.objects.select_related("user").all()
    serializer_class = DoctorProfileSerializer
    filterset_fields = ["specialty"]
    search_fields = ["specialty", "user__username"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
