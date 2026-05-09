import os

base_dir_logistics = r"E:\project\shopconnect\apps\logistics"
base_dir_orders = r"E:\project\shopconnect\apps\orders"
base_dir_users = r"E:\project\shopconnect\apps\users"

# ---------------- LOGISTICS API ----------------

log_permissions_code = """from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff))

class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'driver')
"""

log_serializers_code = """from rest_framework import serializers
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
"""

log_views_code = """from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from .models import Region, ShippingRule, PickupPoint, Shipment, ShipmentTracking, DeliveryAgent
from .serializers import RegionSerializer, ShippingRuleSerializer, PickupPointSerializer, ShipmentSerializer, ShipmentTrackingSerializer, DriverLocationSerializer
from .permissions import IsAdmin, IsDriver

def success_response(data, status_code=status.HTTP_200_OK):
    return Response({"success": True, "data": data}, status=status_code)

def error_response(code, message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "error": {"code": code, "message": message}}, status=status_code)

# --- PUBLIC ---
class RegionListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegionSerializer

    def get_queryset(self):
        qs = Region.objects.filter(deleted_at__isnull=True)
        r_type = self.request.query_params.get('type')
        if r_type:
            qs = qs.filter(type=r_type)
        return qs

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

class ShippingRuleListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ShippingRuleSerializer

    def get_queryset(self):
        qs = ShippingRule.objects.filter(is_active=True, deleted_at__isnull=True)
        from_r = self.request.query_params.get('from_region')
        to_r = self.request.query_params.get('to_region')
        dm = self.request.query_params.get('delivery_method')
        if from_r: qs = qs.filter(from_region_id=from_r)
        if to_r: qs = qs.filter(to_region_id=to_r)
        if dm: qs = qs.filter(delivery_method_id=dm)
        return qs

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

class PickupPointListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PickupPointSerializer

    def get_queryset(self):
        qs = PickupPoint.objects.filter(is_active=True, deleted_at__isnull=True)
        region = self.request.query_params.get('region')
        if region:
            qs = qs.filter(region_id=region)
        return qs

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

# --- ADMIN ---
class AdminShipmentCreateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            shipment = serializer.save()
            return success_response(ShipmentSerializer(shipment).data, status.HTTP_201_CREATED)
        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])

class AdminShipmentStatusUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk, deleted_at__isnull=True)
            status_val = request.data.get('status')
            if not status_val:
                return error_response("VALIDATION_ERROR", "Le champ status est requis.")
            
            shipment.status = status_val
            if status_val == 'in_transit' and not shipment.departure_time:
                shipment.departure_time = timezone.now()
            elif status_val == 'delivered' and not shipment.arrival_time:
                shipment.arrival_time = timezone.now()
            shipment.save()
            return success_response(ShipmentSerializer(shipment).data)
        except Shipment.DoesNotExist:
            return error_response("NOT_FOUND", "Expédition introuvable.", status.HTTP_404_NOT_FOUND)

class AdminShipmentTrackingCreateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk, deleted_at__isnull=True)
            serializer = ShipmentTrackingSerializer(data={**request.data, "shipment": shipment.id})
            if serializer.is_valid():
                tracking = serializer.save(recorded_by=request.user)
                return success_response(ShipmentTrackingSerializer(tracking).data, status.HTTP_201_CREATED)
            field = next(iter(serializer.errors))
            return error_response("VALIDATION_ERROR", serializer.errors[field][0])
        except Shipment.DoesNotExist:
            return error_response("NOT_FOUND", "Expédition introuvable.", status.HTTP_404_NOT_FOUND)

# --- DRIVER ---
class DriverShipmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsDriver]
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        try:
            agent = self.request.user.delivery_agent_profile
            return Shipment.objects.filter(driver=agent, deleted_at__isnull=True).order_by('-created_at')
        except Exception:
            return Shipment.objects.none()

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

class DriverShipmentStatusUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def put(self, request, pk):
        try:
            agent = request.user.delivery_agent_profile
            shipment = Shipment.objects.get(pk=pk, driver=agent, deleted_at__isnull=True)
            status_val = request.data.get('status')
            if not status_val:
                return error_response("VALIDATION_ERROR", "Le champ status est requis.")
            
            shipment.status = status_val
            if status_val == 'in_transit' and not shipment.departure_time:
                shipment.departure_time = timezone.now()
            elif status_val == 'delivered' and not shipment.arrival_time:
                shipment.arrival_time = timezone.now()
            shipment.save()
            
            # Also automatically generate a tracking event
            ShipmentTracking.objects.create(
                shipment=shipment,
                status=f"Mise à jour par le chauffeur: {status_val}",
                recorded_by=request.user,
                latitude=agent.current_latitude,
                longitude=agent.current_longitude
            )
            
            return success_response(ShipmentSerializer(shipment).data)
        except Exception:
            return error_response("NOT_FOUND", "Expédition introuvable ou non assignée.", status.HTTP_404_NOT_FOUND)

class DriverLocationUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def post(self, request):
        serializer = DriverLocationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                agent = request.user.delivery_agent_profile
                agent.current_latitude = serializer.validated_data['latitude']
                agent.current_longitude = serializer.validated_data['longitude']
                agent.location_updated_at = timezone.now()
                agent.save()
                return success_response({"message": "Position mise à jour."})
            except Exception:
                return error_response("NOT_FOUND", "Profil chauffeur introuvable.", status.HTTP_404_NOT_FOUND)
        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])
"""

log_urls_code = """from django.urls import path
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
"""

# ---------------- ORDERS ADDITIONS ----------------
orders_views_additions = """
# ----------- TRACKING ENDPOINT -----------
from apps.logistics.models import ShipmentTracking
from apps.logistics.serializers import ShipmentTrackingSerializer

class OrderTrackingView(views.APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, deleted_at__isnull=True)
            self.check_object_permissions(request, order)
            
            # Find all shipment IDs associated with this order
            shipment_ids = OrderProduct.objects.filter(order=order, shipment__isnull=False).values_list('shipment_id', flat=True).distinct()
            
            # Get all tracking events for these shipments
            trackings = ShipmentTracking.objects.filter(shipment_id__in=shipment_ids).order_by('-timestamp')
            
            return success_response(ShipmentTrackingSerializer(trackings, many=True).data)
        except Order.DoesNotExist:
            return error_response("NOT_FOUND", "Commande introuvable.", status.HTTP_404_NOT_FOUND)
"""

# ---------------- USERS ADMIN API ----------------
users_views_additions = """
# ----------- ADMIN ENDPOINTS -----------
from apps.logistics.permissions import IsAdmin
from apps.users.serializers import UserSerializer
from apps.catalog.pagination import StandardResultsSetPagination

class AdminShopSerializer(serializers.ModelSerializer):
    seller_phone = serializers.CharField(source='seller.user.phone', read_only=True)
    class Meta:
        model = Shop
        fields = ['id', 'name', 'slug', 'seller_phone', 'is_active', 'created_at']

class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = User.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        role = self.request.query_params.get('role')
        status_val = self.request.query_params.get('status')
        if role: qs = qs.filter(role=role)
        if status_val: qs = qs.filter(is_active=(status_val == 'active'))
        return qs

class AdminUserStatusUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk, deleted_at__isnull=True)
            status_val = request.data.get('status') # 'active' or 'suspended'
            if status_val == 'active':
                user.is_active = True
            else:
                user.is_active = False
            user.save()
            return Response({"success": True, "data": {"is_active": user.is_active}})
        except User.DoesNotExist:
            return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Utilisateur introuvable"}}, status=404)

class AdminShopListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminShopSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Shop.objects.filter(deleted_at__isnull=True).order_by('-created_at')

class AdminShopVerifyView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk, deleted_at__isnull=True)
            status_val = request.data.get('status') # 'approved' or 'rejected'
            if status_val == 'approved':
                shop.is_active = True
                shop.seller.is_verified = True
                shop.seller.save()
            else:
                shop.is_active = False
                shop.seller.is_verified = False
                shop.seller.save()
            shop.save()
            return Response({"success": True, "data": {"is_active": shop.is_active}})
        except Shop.DoesNotExist:
            return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Boutique introuvable"}}, status=404)
"""

def append_to_file(filepath, content):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

# Files creation
files = {
    os.path.join(base_dir_logistics, "permissions.py"): log_permissions_code,
    os.path.join(base_dir_logistics, "serializers.py"): log_serializers_code,
    os.path.join(base_dir_logistics, "views.py"): log_views_code,
    os.path.join(base_dir_logistics, "urls.py"): log_urls_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

append_to_file(os.path.join(base_dir_orders, "views.py"), orders_views_additions)
append_to_file(os.path.join(base_dir_users, "views.py"), users_views_additions)

print("Level 7 scripts generated successfully.")
