from typing import Optional

from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.customers.models import Customer
from apps.orgs.models import Store

from .models import DeviceType, RepairLineItem, RepairOrder
from .serializers import DeviceTypeSerializer, RepairLineItemSerializer, RepairOrderSerializer


class RepairOrderViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    queryset = RepairOrder.objects.all()
    serializer_class = RepairOrderSerializer

    @action(detail=True, methods=["post"], url_path="line-items")
    def add_line_item(self, request, pk: Optional[str] = None):
        repair = self.get_object()
        serializer = RepairLineItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RepairLineItem.objects.create(repair=repair, **serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PublicRepairTrackView(generics.RetrieveAPIView):
    serializer_class = RepairOrderSerializer
    lookup_field = "public_lookup_token"
    lookup_url_kwarg = "token"

    def get_queryset(self):
        return RepairOrder.objects.all()


class IntakeCreateView(generics.CreateAPIView):
    serializer_class = RepairOrderSerializer

    def create(self, request, *args, **kwargs):
        store_id = getattr(request, "store_id", None)
        if not store_id:
            return Response({"detail": "Missing X-Store-ID"}, status=status.HTTP_400_BAD_REQUEST)
        store = get_object_or_404(Store, id=store_id)
        data = request.data or {}
        cust_input = data.get("customer") or {}
        email = cust_input.get("email")
        first_name = cust_input.get("first_name", "")
        last_name = cust_input.get("last_name", "")
        phone = cust_input.get("phone")
        customer = None
        if email:
            customer = Customer.objects.filter(email=email).first()
        if not customer:
            customer = Customer.objects.create(
                email=email, first_name=first_name, last_name=last_name, phone=phone
            )
        device = data.get("device") or {}
        repair = RepairOrder.objects.create(
            store=store,
            customer=customer,
            device_make=device.get("make") or "",
            device_model=device.get("model"),
            device_serial=device.get("serial"),
            issue_description=data.get("issue_description"),
            public_lookup_token=customer.id.hex[
                :20
            ],  # simple stable token; can be randomized later
        )
        serializer = self.get_serializer(repair)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceTypeListView(generics.ListAPIView):
    serializer_class = DeviceTypeSerializer

    def get_queryset(self):
        return DeviceType.objects.all().order_by("name")
