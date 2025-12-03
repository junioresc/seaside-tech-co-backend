from rest_framework import serializers

from .models import Appointment, ServiceType


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["code", "name", "default_duration_minutes", "estimated_price_cents"]


class AppointmentSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "status", "start_at", "end_at", "service_type", "checkin_token"]
