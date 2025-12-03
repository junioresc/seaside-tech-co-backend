from django.conf import settings
from django.db import models

from encrypted_fields.fields import EncryptedTextField

from apps.common.models import BaseModel


class Customer(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer",
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = EncryptedTextField(null=True, blank=True)
    address = EncryptedTextField(null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    invited = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.first_name} {self.last_name}"
