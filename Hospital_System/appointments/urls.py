from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    BlogViewSet,
    ContactView,
    EmergencyCareViewSet,
    OnlineConsultationViewSet,
    PhysicalAppointmentViewSet,
)

router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"physical-appointments", PhysicalAppointmentViewSet, basename="physical")
router.register(r"emergency-care", EmergencyCareViewSet, basename="emergency")
router.register(r"online-consultations", OnlineConsultationViewSet, basename="online-consultation")
router.register(r"blog", BlogViewSet, basename="blog")

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("", include(router.urls)),
]
