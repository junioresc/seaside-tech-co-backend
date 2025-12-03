from rest_framework import generics

from .models import Appointment, ServiceType
from .serializers import AppointmentSerializer, ServiceTypeSerializer


class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        return super().create(request, *args, **kwargs)


class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.all().order_by("start_at")


class AppointmentCheckinView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        return super().create(request, *args, **kwargs)


class ServiceTypeListView(generics.ListAPIView):
    serializer_class = ServiceTypeSerializer

    def get_queryset(self):
        return ServiceType.objects.all().order_by("name")
