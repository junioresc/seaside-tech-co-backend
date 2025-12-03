from django.utils import timezone

from celery import shared_task

from apps.appointments.models import Appointment
from apps.notifications.services import EmailSender


@shared_task
def send_appointment_reminder_task(appointment_id: str) -> None:
    appt = Appointment.objects.select_related("customer", "store").filter(id=appointment_id).first()
    if not appt or not appt.customer or not appt.customer.email:
        return
    start_local = timezone.localtime(appt.start_at).strftime("%Y-%m-%d %H:%M")
    context = {
        "customer": {"first_name": appt.customer.first_name},
        "appointment": {"start_at_local": start_local},
        "store": appt.store,
    }
    EmailSender().send_template(
        [appt.customer.email],
        "Appointment reminder",
        "notifications/appointment_reminder.html",
        context,
    )
