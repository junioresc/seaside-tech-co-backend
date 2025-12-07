from decimal import Decimal

from django.db import models

from apps.common.models import BaseModel
from apps.orgs.models import Store


class ServiceType(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    default_duration_minutes = models.IntegerField(default=30)
    estimated_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Appointment(BaseModel):
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name="appointments")
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.SET_NULL, null=True, blank=True
    )
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ("booked", "booked"),
            ("confirmed", "confirmed"),
            ("cancelled", "cancelled"),
            ("completed", "completed"),
        ],
        default="booked",
    )
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        "users.UserProfile", on_delete=models.SET_NULL, null=True, blank=True
    )
    assigned_technician = models.ForeignKey(
        "technicians.Technician", on_delete=models.SET_NULL, null=True, blank=True
    )
    checkin_token = models.CharField(max_length=64, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
