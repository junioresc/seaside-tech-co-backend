from django.db import models

from apps.common.models import BaseModel
from apps.users.models import UserProfile


class Technician(BaseModel):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="technician")
    certifications = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Tech: {self.profile.user.get_username()}"


