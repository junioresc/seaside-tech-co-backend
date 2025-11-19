from django.db import models

from apps.common.models import BaseModel
from simple_history.models import HistoricalRecords
from decimal import Decimal


class Product(BaseModel):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")
    inventory_count = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    images = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.sku} - {self.name}"


class ProductInventory(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")
    store = models.ForeignKey("orgs.Store", on_delete=models.CASCADE, related_name="product_inventories")
    quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    history = HistoricalRecords()

    class Meta:
        unique_together = ("product", "store")


