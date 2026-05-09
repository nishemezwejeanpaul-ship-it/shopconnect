from django.urls import path
from .views import (
    RegionListView, ShippingRuleListView, PickupPointListView,
    AdminShipmentCreateView, AdminShipmentStatusUpdateView, AdminShipmentTrackingCreateView,
    DriverShipmentListView, DriverShipmentStatusUpdateView, DriverLocationUpdateView
)

urlpatterns = [
    # Public
    path('regions/', RegionListView.as_view(), name='region_list'),
    path('shipping-rules/', ShippingRuleListView.as_view(), name='shipping_rule_list'),
    path('pickup-points/', PickupPointListView.as_view(), name='pickup_point_list'),

    # Admin
    path('admin/shipments/', AdminShipmentCreateView.as_view(), name='admin_shipment_create'),
    path('admin/shipments/<uuid:pk>/status/', AdminShipmentStatusUpdateView.as_view(), name='admin_shipment_status_update'),
    path('admin/shipments/<uuid:pk>/tracking/', AdminShipmentTrackingCreateView.as_view(), name='admin_shipment_tracking_create'),

    # Driver
    path('driver/shipments/', DriverShipmentListView.as_view(), name='driver_shipment_list'),
    path('driver/shipments/<uuid:pk>/status/', DriverShipmentStatusUpdateView.as_view(), name='driver_shipment_status_update'),
    path('driver/location/', DriverLocationUpdateView.as_view(), name='driver_location_update'),
]
