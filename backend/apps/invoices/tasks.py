from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.loader import render_to_string

from celery import shared_task
from weasyprint import HTML

from apps.invoices.models import Invoice
from apps.repairs.models import RepairLineItem


@shared_task
def generate_invoice_pdf_task(invoice_id: str) -> None:
    inv = Invoice.objects.select_related("repair", "repair__customer").filter(id=invoice_id).first()
    if not inv:
        return
    line_items = list(
        RepairLineItem.objects.filter(repair=inv.repair).values(
            "description", "quantity", "unit_price"
        )
    )
    html = render_to_string(
        "invoices/invoice.html",
        {
            "invoice": inv,
            "line_items": line_items,
        },
    )
    pdf_bytes = HTML(string=html).write_pdf()
    path = f"invoices/{inv.id}.pdf"
    default_storage.save(path, ContentFile(pdf_bytes))
    inv.pdf_url = default_storage.url(path)
    inv.save(update_fields=["pdf_url"])
