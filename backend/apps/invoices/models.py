from decimal import Decimal

from django.db import models

from simple_history.models import HistoricalRecords

from apps.common.models import BaseModel


class Invoice(BaseModel):
    repair = models.OneToOneField(
        "repairs.RepairOrder", on_delete=models.CASCADE, related_name="invoice"
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid = models.BooleanField(default=False)
    stripe_payment_intent = models.CharField(max_length=200, null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)
    history = HistoricalRecords()
