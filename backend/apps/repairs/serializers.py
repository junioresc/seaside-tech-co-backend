from rest_framework import serializers

from .models import DeviceType, RepairLineItem, RepairOrder


class RepairLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairLineItem
        fields = ["id", "description", "quantity", "unit_price", "product"]


class RepairOrderSerializer(serializers.ModelSerializer):
    line_items = RepairLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = RepairOrder
        fields = [
            "id",
            "status",
            "device_make",
            "device_model",
            "device_serial",
            "issue_description",
            "public_lookup_token",
            "created",
            "line_items",
        ]


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["code", "name"]


