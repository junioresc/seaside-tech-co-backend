from __future__ import annotations

from celery import shared_task

from apps.notifications.services import EmailSender, SMSSender
from apps.repairs.models import RepairOrder


@shared_task
def send_repair_status_email_task(repair_id: str) -> None:
    repair = RepairOrder.objects.select_related("customer").filter(id=repair_id).first()
    if not repair or not repair.customer or not repair.customer.email:
        return
    public_url = (
        f"/api/v1/repairs/track/{repair.public_lookup_token}" if repair.public_lookup_token else ""
    )
    context = {"customer": repair.customer, "repair": repair, "public_url": public_url}
    EmailSender().send_template(
        [repair.customer.email],
        "Repair status updated",
        "notifications/repair_status_changed.html",
        context,
    )


@shared_task
def send_sms_task(phone_e164: str, message: str) -> None:
    SMSSender().send(phone_e164, message)
