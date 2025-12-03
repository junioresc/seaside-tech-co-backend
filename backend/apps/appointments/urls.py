from django.urls import path

from .views import (
    AppointmentCheckinView,
    AppointmentCreateView,
    AppointmentListView,
    ServiceTypeListView,
)

urlpatterns = [
    path("appointments/", AppointmentCreateView.as_view(), name="appointment-create"),
    path("appointments/list/", AppointmentListView.as_view(), name="appointment-list"),
    path(
        "appointments/<uuid:id>/checkin/",
        AppointmentCheckinView.as_view(),
        name="appointment-checkin",
    ),
    path("reference/service-types/", ServiceTypeListView.as_view(), name="service-type-list"),
]
