from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import DoctorProfile
from .models import Appointment, Blog, EmergencyCare, PhysicalAppointment, online_doctor
from .permissions import IsAdminOrCreateOnly, IsAdminOrReadOnly
from .serializers import (
    AppointmentSerializer,
    BlogSerializer,
    ContactSerializer,
    EmergencyCareSerializer,
    OnlineConsultationSerializer,
    PhysicalAppointmentSerializer,
)

WEEKDAY_SLOTS = [(8, 9), (10, 11), (12, 13), (14, 15), (16, 17)]


class _BookingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Public booking submissions; staff can list/inspect them."""

    permission_classes = [IsAdminOrCreateOnly]


class PhysicalAppointmentViewSet(_BookingViewSet):
    queryset = PhysicalAppointment.objects.all().order_by("-created_at")
    serializer_class = PhysicalAppointmentSerializer

    def perform_create(self, serializer):
        appt = serializer.save()
        send_mail(
            "Booking Confirmation",
            f"Dear {appt.name},\n\nYour {appt.service_needed} appointment on "
            f"{appt.appointment_date} is confirmed.\n\nCoast General Hospital",
            settings.DEFAULT_FROM_EMAIL,
            [appt.email],
            fail_silently=True,
        )


class EmergencyCareViewSet(_BookingViewSet):
    queryset = EmergencyCare.objects.all().order_by("-timestamp")
    serializer_class = EmergencyCareSerializer


class OnlineConsultationViewSet(_BookingViewSet):
    queryset = online_doctor.objects.all().order_by("-date")
    serializer_class = OnlineConsultationSerializer


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by("-id")
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["title", "description"]


class AppointmentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """A logged-in patient's typed, time-slot appointments."""

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        appt = serializer.save(patient=self.request.user)
        if self.request.user.email:
            send_mail(
                "Appointment Confirmation",
                f"Dear {self.request.user.username},\n\nYour {appt.appointment_type} "
                f"appointment is scheduled for {appt.appointment_time}.\n\n"
                f"Coast General Hospital",
                settings.DEFAULT_FROM_EMAIL,
                [self.request.user.email],
                fail_silently=True,
            )

    @extend_schema(responses={200: OpenApiResponse(description="Available appointment types.")})
    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def types(self, request):
        """Appointment types, derived from the specialties doctors offer."""
        specialties = list(
            DoctorProfile.objects.values_list("specialty", flat=True).distinct()
        )
        return Response({"types": specialties})

    @extend_schema(
        parameters=[OpenApiParameter("type", str, required=True)],
        responses={200: OpenApiResponse(description="Available time slots.")},
    )
    @action(detail=False, methods=["get"])
    def slots(self, request):
        """Free weekday slots (next 5 days) for a given appointment type."""
        appt_type = request.query_params.get("type", "")
        now = datetime.now()
        today = now.date()
        available, booked = [], []
        for i in range(5):
            day = today + timedelta(days=i)
            if day.weekday() >= 5:
                continue
            for start_hour, _ in WEEKDAY_SLOTS:
                slot = datetime.combine(day, time(start_hour, 0))
                if slot < now:
                    continue
                exists = Appointment.objects.filter(
                    appointment_time=slot, appointment_type=appt_type
                ).exists()
                (booked if exists else available).append(slot.isoformat())
        return Response({"type": appt_type, "available": available, "booked": booked})

    @extend_schema(responses={200: AppointmentSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="for-doctor")
    def for_doctor(self, request):
        """Appointments matching the authenticated doctor's specialty."""
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response(
                {"detail": "You do not have a doctor profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = Appointment.objects.filter(appointment_type__iexact=doctor.specialty)
        return Response(AppointmentSerializer(qs, many=True).data)


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ContactSerializer, responses={200: OpenApiResponse(description="Sent.")})
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_mail(
            subject=f"[Contact] {data['subject']}",
            message=f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
            fail_silently=True,
        )
        return Response({"detail": "Thank you for contacting us. We'll respond shortly."})
