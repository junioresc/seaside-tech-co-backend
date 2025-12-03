from decimal import Decimal

from django.db import models

from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import StatusModel
from simple_history.models import HistoricalRecords

from apps.common.models import BaseModel
from apps.customers.models import Customer
from apps.orgs.models import Store
from apps.products.models import Product
from apps.technicians.models import Technician
from apps.users.models import UserProfile


class DeviceType(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)

    def __str__(self) -> str:  # pragma: no cover
        return self.name

class RepairStatusMixin:
    """Mixin to provide STATUS choices for RepairOrder history."""
    STATUS = Choices(
        ("received", "Received"),
        ("diagnosing", "Diagnosing"),
        ("awaiting_approval", "Awaiting approval"),
        ("approved", "Approved"),
        ("repairing", "Repairing"),
        ("waiting_parts", "Waiting for parts"),
        ("ready", "Ready for pickup"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("scheduled", "Scheduled"),
        ("checked_in", "Checked in"),
        ("in_progress", "In progress"),
    )


class RepairOrder(RepairStatusMixin, StatusModel, BaseModel):

    status = StatusField(default=RepairStatusMixin.STATUS.received)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name="repairs")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="repairs")
    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name="repairs"
    )
    intake_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    device_make = models.CharField(max_length=120)
    device_model = models.CharField(max_length=120, null=True, blank=True)
    device_serial = models.CharField(max_length=120, null=True, blank=True, db_index=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True, blank=True)
    issue_description = models.TextField(null=True, blank=True)
    estimated_cost_cents = models.IntegerField(null=True, blank=True)
    actual_cost_cents = models.IntegerField(null=True, blank=True)
    pickup_code = models.CharField(max_length=12, null=True, blank=True)
    label_data = models.JSONField(null=True, blank=True)
    public_lookup_token = models.CharField(max_length=64, null=True, blank=True)
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repairs",
    )
    history = HistoricalRecords(bases=[RepairStatusMixin])

    def __str__(self) -> str:  # pragma: no cover
        return f"Repair {self.id} - {self.status}"


class RepairLineItem(BaseModel):
    repair = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=300)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()
