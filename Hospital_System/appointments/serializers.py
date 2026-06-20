from rest_framework import serializers

from .models import Appointment, Blog, EmergencyCare, PhysicalAppointment, online_doctor


class PhysicalAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalAppointment
        fields = (
            "id", "name", "email", "phone_no", "service_needed",
            "appointment_date", "created_at",
        )
        read_only_fields = ("id", "created_at")


class EmergencyCareSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyCare
        fields = (
            "id", "patient_name", "contact_number", "condition_description",
            "priority_level", "location", "timestamp",
        )
        read_only_fields = ("id", "timestamp")


class OnlineConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = online_doctor
        fields = ("id", "name", "email", "phone_number", "service_type", "date", "time")
        read_only_fields = ("id",)


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ("id", "title", "description", "image")


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Appointment
        fields = ("id", "patient", "appointment_type", "appointment_time", "booked_at")
        read_only_fields = ("id", "patient", "booked_at")


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
