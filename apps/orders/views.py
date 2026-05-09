from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Cart, Order, OrderItem, OrderProduct
from apps.catalog.models import Product, ProductVariant
from .serializers import (
    CartSerializer, CartAddSerializer, CartUpdateSerializer, OrderSerializer,
    DeliveryMethodSerializer, ShippingAddressSerializer
)
from .permissions import IsOwner

def success_response(data, status_code=status.HTTP_200_OK):
    return Response({"success": True, "data": data}, status=status_code)

def error_response(code, message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }, status=status_code)

class CartListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, deleted_at__isnull=True).select_related('product', 'product__shop', 'product__category')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class CartAddView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            quantity = serializer.validated_data['quantity']

            # Check if product exists
            try:
                product = Product.objects.get(id=product_id, deleted_at__isnull=True, status='active')
            except Product.DoesNotExist:
                return error_response("NOT_FOUND", "Produit introuvable.", status.HTTP_404_NOT_FOUND)

            # Check variant if provided
            if variant_id:
                try:
                    ProductVariant.objects.get(id=variant_id, product=product, deleted_at__isnull=True)
                except ProductVariant.DoesNotExist:
                    return error_response("NOT_FOUND", "Variante introuvable.", status.HTTP_404_NOT_FOUND)

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product_id=product_id,
                variant_id=variant_id,
                deleted_at__isnull=True,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return success_response(CartSerializer(cart_item).data, status.HTTP_201_CREATED)

        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])

class CartUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = CartUpdateSerializer

    def get_queryset(self):
        return Cart.objects.filter(deleted_at__isnull=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(CartSerializer(instance).data)
        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])

class CartRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Cart.objects.filter(deleted_at__isnull=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return success_response(None)

from apps.logistics.models import Region, PickupPoint, ShippingRule, HubLocation
from .models import Cart, Order, OrderItem, OrderProduct, DeliveryMethod, ShippingAddress

class ShippingCalculationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        method_code = request.data.get('delivery_method_code')
        to_region_id = request.data.get('to_region_id')
        pickup_point_id = request.data.get('pickup_point_id')

        if not method_code or not to_region_id:
            return error_response("VALIDATION_ERROR", "delivery_method_code et to_region_id sont requis.")

        try:
            method = DeliveryMethod.objects.get(code=method_code, is_active=True)
            to_region = Region.objects.get(id=to_region_id)
        except (DeliveryMethod.DoesNotExist, Region.DoesNotExist):
            return error_response("NOT_FOUND", "Méthode de livraison ou région introuvable.")

        shipping_fee = None
        available = False
        estimated_days = 0

        # Logic based on Business Model
        is_buj_zone = to_region.type == 'zone' and to_region.parent and to_region.parent.name == "Bujumbura City"

        if method_code == 'DOOR_FREE':
            # available ONLY in Bujumbura urban zones
            if is_buj_zone:
                available = True
                shipping_fee = Decimal('0.00')
                estimated_days = 1
            else:
                available = False
        
        elif method_code == 'PICKUP_FREE':
            # available for all regions, requires pickup_point_id
            if pickup_point_id:
                try:
                    PickupPoint.objects.get(id=pickup_point_id, is_active=True)
                    available = True
                    shipping_fee = Decimal('0.00')
                    estimated_days = 2
                except PickupPoint.DoesNotExist:
                    return error_response("NOT_FOUND", "Point de retrait introuvable.")
            else:
                return error_response("VALIDATION_ERROR", "pickup_point_id est requis pour le retrait en point relais.")

        elif method_code == 'DOOR_EXPRESS':
            # only available in Bujumbura urban zones
            if is_buj_zone:
                # lookup ShippingRule
                try:
                    buj_city = Region.objects.get(name="Bujumbura City", type="city")
                    rule = ShippingRule.objects.get(from_region=buj_city, to_region=to_region, delivery_method=method, is_active=True)
                    available = True
                    shipping_fee = rule.price
                    estimated_days = 0 # 2-4 hours
                except (Region.DoesNotExist, ShippingRule.DoesNotExist):
                    available = False
            else:
                available = False

        return success_response({
            "shipping_fee": shipping_fee,
            "method_name": method.name,
            "estimated_days": estimated_days,
            "available": available
        })

class OrderCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        method_code = request.data.get('delivery_method_code')
        shipping_address_id = request.data.get('shipping_address_id')
        pickup_point_id = request.data.get('pickup_point_id')

        if not method_code:
            return error_response("VALIDATION_ERROR", "delivery_method_code est requis.")

        try:
            method = DeliveryMethod.objects.get(code=method_code, is_active=True)
        except DeliveryMethod.DoesNotExist:
            return error_response("NOT_FOUND", "Méthode de livraison introuvable.")

        # Validate Address/Pickup based on method
        shipping_address = None
        pickup_point = None
        to_region = None

        if method_code == 'PICKUP_FREE':
            if not pickup_point_id:
                return error_response("VALIDATION_ERROR", "pickup_point_id est requis.")
            try:
                pickup_point = PickupPoint.objects.get(id=pickup_point_id, is_active=True)
                to_region = pickup_point.region
            except PickupPoint.DoesNotExist:
                return error_response("NOT_FOUND", "Point de retrait introuvable.")
        else:
            if not shipping_address_id:
                return error_response("VALIDATION_ERROR", "shipping_address_id est requis.")
            try:
                shipping_address = ShippingAddress.objects.get(id=shipping_address_id, user=user)
                to_region = shipping_address.region
            except ShippingAddress.DoesNotExist:
                return error_response("NOT_FOUND", "Adresse de livraison introuvable.")

        # Calculate shipping fee again to be sure
        shipping_fee = Decimal('0.00')
        is_buj_zone = to_region.type == 'zone' and to_region.parent and to_region.parent.name == "Bujumbura City"

        if method_code == 'DOOR_EXPRESS':
            if not is_buj_zone:
                return error_response("INVALID_LOGISTICS", "La livraison express est uniquement disponible dans les zones urbaines de Bujumbura.")
            try:
                buj_city = Region.objects.get(name="Bujumbura City", type="city")
                rule = ShippingRule.objects.get(from_region=buj_city, to_region=to_region, delivery_method=method, is_active=True)
                shipping_fee = rule.price
            except ShippingRule.DoesNotExist:
                return error_response("INVALID_LOGISTICS", "Cette méthode n'est pas disponible pour cette région.")
        
        elif method_code == 'DOOR_FREE':
            if not is_buj_zone:
                return error_response("INVALID_LOGISTICS", "La livraison à domicile gratuite est uniquement disponible dans les zones urbaines de Bujumbura.")

        # Lock cart items
        cart_items = Cart.objects.filter(user=user, deleted_at__isnull=True).select_for_update()
        if not cart_items.exists():
            return error_response("EMPTY_CART", "Votre panier est vide.")

        # Gather product and variant IDs
        product_ids = [item.product_id for item in cart_items]
        variant_ids = [item.variant_id for item in cart_items if item.variant_id]

        # Lock products and variants
        products = Product.objects.filter(id__in=product_ids).select_for_update()
        product_map = {p.id: p for p in products}

        variant_map = {}
        if variant_ids:
            variants = ProductVariant.objects.filter(id__in=variant_ids).select_for_update()
            variant_map = {v.id: v for v in variants}

        # 1. Check Stock
        for item in cart_items:
            prod = product_map.get(item.product_id)
            if not prod or prod.status != 'active':
                return error_response("PRODUCT_UNAVAILABLE", f"Le produit {prod.name if prod else 'inconnu'} n'est plus disponible.")

            if item.variant_id:
                var = variant_map.get(item.variant_id)
                available_stock = var.stock_quantity
                name = f"{prod.name} ({var.name})"
            else:
                available_stock = prod.stock_quantity
                name = prod.name

            if available_stock < item.quantity:
                return error_response("OUT_OF_STOCK", f"Le produit {name} n'est plus disponible en quantité suffisante.")

        # 2. Create Order
        currency = 'BIF'
        if products:
            currency = products[0].currency

        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            pickup_point=pickup_point,
            final_delivery_method=method,
            subtotal=0,
            shipping_fee=shipping_fee,
            total_amount=0,
            currency=currency,
            status='pending'
        )

        subtotal = Decimal('0.00')

        # 3. Deduct stock and create items
        for item in cart_items:
            prod = product_map[item.product_id]
            base_price = prod.discount_price if prod.discount_price else prod.price
            variant_price = Decimal('0.00')

            if item.variant_id:
                var = variant_map[item.variant_id]
                variant_price = var.additional_price
                var.stock_quantity -= item.quantity
                var.save()

            prod.stock_quantity -= item.quantity
            prod.save()

            unit_price = base_price + variant_price
            total_price = unit_price * item.quantity
            subtotal += total_price

            order_item = OrderItem.objects.create(
                order=order,
                product=prod,
                variant_id=item.variant_id,
                shop=prod.shop,
                quantity=item.quantity,
                unit_price=unit_price,
                total_price=total_price
            )

            OrderProduct.objects.create(
                order=order,
                order_item=order_item,
                product=prod,
                shop=prod.shop,
                status='pending'
            )

        # 4. Finalize order
        order.subtotal = subtotal
        order.total_amount = subtotal + shipping_fee
        order.save()

        # 5. Clear cart (soft delete)
        cart_items.update(deleted_at=timezone.now())

        # Fetch fully populated order
        order_data = Order.objects.prefetch_related('items', 'items__product').get(id=order.id)
        return success_response(OrderSerializer(order_data).data, status.HTTP_201_CREATED)

class DeliveryMethodListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryMethodSerializer
    queryset = DeliveryMethod.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class ShippingAddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user, deleted_at__isnull=True)

    def perform_create(self, serializer):
        # If this is default, unset other defaults
        if serializer.validated_data.get('is_default'):
            ShippingAddress.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(serializer.data, status.HTTP_201_CREATED)
        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", f"{field}: {serializer.errors[field][0]}")

class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, deleted_at__isnull=True).prefetch_related('items').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(deleted_at__isnull=True).prefetch_related(
            'items', 'items__product', 'items__product__images'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

# ----------- SELLER ENDPOINTS -----------
from apps.catalog.permissions import IsSeller
from django.db.models import Prefetch

class SellerOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    serializer_class = OrderSerializer

    def get_queryset(self):
        shop = self.request.user.seller_profile.shop
        # Get orders that contain products from this shop
        orders = Order.objects.filter(
            order_products__shop=shop, 
            deleted_at__isnull=True
        ).distinct()

        # Prefetch only this shop's items
        prefetch_items = Prefetch('items', queryset=OrderItem.objects.filter(shop=shop))
        return orders.prefetch_related(prefetch_items).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class SellerOrderStatusUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    def put(self, request, pk):
        shop = request.user.seller_profile.shop
        status_val = request.data.get('status')
        order_product_id = request.data.get('order_product_id')

        if not status_val:
            return error_response("VALIDATION_ERROR", "Le champ status est requis.")

        try:
            if order_product_id:
                # Update specific product in the order
                op = OrderProduct.objects.get(id=order_product_id, order_id=pk, shop=shop)
                op.status = status_val
                op.save()
            else:
                # Update all products in this order belonging to the shop
                ops = OrderProduct.objects.filter(order_id=pk, shop=shop)
                if not ops.exists():
                    return error_response("NOT_FOUND", "Aucun produit trouvé pour cette commande.")
                ops.update(status=status_val)
                
            return success_response({"message": "Statut mis à jour."})
        except OrderProduct.DoesNotExist:
            return error_response("NOT_FOUND", "Produit introuvable.", status.HTTP_404_NOT_FOUND)

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
