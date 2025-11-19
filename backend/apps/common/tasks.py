from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from apps.audit.models import AuditLog


@shared_task
def retention_cleanup_task(days: int = 365) -> None:
    cutoff = timezone.now() - timedelta(days=days)
    AuditLog.objects.filter(created__lt=cutoff).delete()


