from django.db.models import F

from celery import shared_task

from apps.notifications.services import EmailSender
from apps.products.models import ProductInventory


@shared_task
def low_stock_check_task() -> None:
    low_items = ProductInventory.objects.select_related(
        "product", "store", "store__organization"
    ).filter(quantity__lte=F("low_stock_threshold"))
    if not low_items.exists():
        return
    sender = EmailSender()
    for inv in low_items:
        org_email = getattr(inv.store.organization, "billing_email", None)
        if not org_email:
            continue
        context = {
            "product": inv.product,
            "store": inv.store,
            "quantity": inv.quantity,
            "threshold": inv.low_stock_threshold,
        }
        sender.send_template(
            [org_email], "Low stock alert", "notifications/low_stock_alert.html", context
        )
