from django.contrib import admin
from .models import Region, HubLocation, PickupPoint, DeliveryAgent, ShippingRule, Shipment, ShipmentItem, ShipmentTracking

admin.site.register(Region)
admin.site.register(HubLocation)
admin.site.register(PickupPoint)
admin.site.register(DeliveryAgent)
admin.site.register(ShippingRule)
admin.site.register(Shipment)
admin.site.register(ShipmentItem)
admin.site.register(ShipmentTracking)
