from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    tax_id = models.CharField(max_length=64, null=True, blank=True)
    billing_email = models.EmailField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Store(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=200)
    address = models.JSONField(null=True, blank=True)
    timezone = models.CharField(max_length=64, default="America/Los_Angeles")
    phone = models.CharField(max_length=30, null=True, blank=True)
    business_hours = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.organization.name})"


class Membership(BaseModel):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("tech", "Technician"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "store")
