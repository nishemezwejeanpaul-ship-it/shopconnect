from rest_framework import serializers
from .models import Region, ShippingRule, PickupPoint, Shipment, ShipmentTracking, DeliveryAgent

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'type', 'parent']

class ShippingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRule
        fields = ['id', 'from_region', 'to_region', 'delivery_method', 'price', 'estimated_days', 'currency']

class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoint
        fields = ['id', 'name', 'region', 'address', 'phone', 'type']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'hub_from', 'hub_to', 'driver', 'status', 'departure_time', 'arrival_time', 'notes']

class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = ['id', 'shipment', 'status', 'latitude', 'longitude', 'timestamp']

class DriverLocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
