from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.common.models import BaseModel

User = get_user_model()


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=30,
        choices=[("customer", "customer"), ("tech", "technician"), ("admin", "admin")],
        default="customer",
    )
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/%d/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )
    avatar_thumb = models.ImageField(upload_to="avatars/thumbs/%Y/%m/%d/", null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.get_username()} ({self.role})"
