from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceTypeListView, IntakeCreateView, PublicRepairTrackView, RepairOrderViewSet

router = DefaultRouter()
router.register(r"repairs", RepairOrderViewSet, basename="repair")

urlpatterns = [
    path("", include(router.urls)),
    path("repairs/track/<str:token>", PublicRepairTrackView.as_view(), name="repair-track"),
    path("intake/", IntakeCreateView.as_view(), name="intake"),
    path("reference/device-types/", DeviceTypeListView.as_view(), name="device-type-list"),
]


