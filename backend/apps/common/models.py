import uuid
from model_utils.models import TimeStampedModel
from django.db import models


class BaseModel(TimeStampedModel, models.Model):
    """
    Shared base that provides UUID primary keys and the richer created/modified
    behavior from model_utils' TimeStampedModel.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True
