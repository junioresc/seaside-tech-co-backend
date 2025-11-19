from django.db import models

from apps.common.models import BaseModel
from apps.orgs.models import Store


class InventoryTransaction(BaseModel):
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="transactions")
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name="inventory_transactions")
    change = models.IntegerField()
    reason = models.CharField(max_length=120)
    related_order = models.ForeignKey(
        "repairs.RepairOrder", on_delete=models.SET_NULL, null=True, blank=True
    )


