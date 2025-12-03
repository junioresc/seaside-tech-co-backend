from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from apps.orgs.models import Store


class AuditLog(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=120)
    model = models.CharField(max_length=120)
    object_pk = models.CharField(max_length=120)
    changes = models.JSONField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
