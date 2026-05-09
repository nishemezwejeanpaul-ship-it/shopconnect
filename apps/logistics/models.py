import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import BaseModel

class Region(BaseModel):
    TYPE_CHOICES = (
        ('province', 'Province'),
        ('city', 'City'),
        ('zone', 'Zone'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_regions')

    def __str__(self):
        return self.name

class HubLocation(BaseModel):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PickupPoint(BaseModel):
    TYPE_CHOICES = (
        ('shop', 'Shop'),
        ('partner', 'Partner'),
        ('locker', 'Locker'),
    )
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DeliveryAgent(BaseModel):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('on_delivery', 'On Delivery'),
        ('offline', 'Offline'),
    )
    VEHICLE_CHOICES = (
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('van', 'Van'),
    )
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='delivery_agent_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, null=True, blank=True)
    license_plate = models.CharField(max_length=30, blank=True)
    hub = models.ForeignKey(HubLocation, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Driver: {self.user.phone}"

class ShippingRule(BaseModel):
    from_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='rules_from')
    to_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='rules_to')
    delivery_method = models.ForeignKey('orders.DeliveryMethod', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    estimated_days = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='BIF')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('from_region', 'to_region', 'delivery_method')

    def __str__(self):
        return f"{self.from_region} -> {self.to_region}"

class Shipment(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    hub_from = models.ForeignKey(HubLocation, on_delete=models.PROTECT, related_name='shipments_origin')
    hub_to = models.ForeignKey(HubLocation, on_delete=models.PROTECT, related_name='shipments_dest')
    driver = models.ForeignKey(DeliveryAgent, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Shipment {self.id}"

class ShipmentItem(BaseModel):
    STATUS_CHOICES = (
        ('packed', 'Packed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('lost', 'Lost'),
    )
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    order_product = models.ForeignKey('orders.OrderProduct', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='packed')

    class Meta:
        unique_together = ('shipment', 'order_product')

class ShipmentTracking(BaseModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    recorded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
