from rest_framework import generics, status, views
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
