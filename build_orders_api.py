import os

base_dir = r"E:\project\shopconnect\apps\orders"

permissions_code = """from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.user == request.user)
"""

serializers_code = """from rest_framework import serializers
from .models import Cart, Order, OrderItem, OrderProduct
from apps.catalog.serializers import ProductListSerializer

class CartSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'product', 'variant', 'quantity', 'coupon_code', 'product_details', 'created_at']
        read_only_fields = ['id', 'created_at']

class CartAddSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variant', 'shop', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'subtotal', 'discount_amount', 'total_amount', 'currency', 'status', 'created_at', 'items']
"""

views_code = """from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Cart, Order, OrderItem, OrderProduct
from apps.catalog.models import Product, ProductVariant
from .serializers import CartSerializer, CartAddSerializer, CartUpdateSerializer, OrderSerializer
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

class OrderCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        
        # Lock cart items
        cart_items = Cart.objects.filter(user=user, deleted_at__isnull=True).select_for_update()
        
        if not cart_items.exists():
            return error_response("EMPTY_CART", "Votre panier est vide.")

        # Gather product and variant IDs
        product_ids = [item.product_id for item in cart_items]
        variant_ids = [item.variant_id for item in cart_items if item.variant_id]

        # Lock products and variants to prevent race conditions on stock
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
            subtotal=0,
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
        order.total_amount = subtotal
        order.save()

        # 5. Clear cart (soft delete)
        cart_items.update(deleted_at=timezone.now())

        # Fetch fully populated order
        order_data = Order.objects.prefetch_related('items', 'items__product').get(id=order.id)
        return success_response(OrderSerializer(order_data).data, status.HTTP_201_CREATED)

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
        return Order.objects.filter(deleted_at__isnull=True).prefetch_related('items')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)
"""

urls_code = """from django.urls import path
from .views import (
    CartListView, CartAddView, CartUpdateView, CartRemoveView,
    OrderCreateView, OrderListView, OrderDetailView
)

urlpatterns = [
    path('cart/', CartListView.as_view(), name='cart_list'),
    path('cart/add/', CartAddView.as_view(), name='cart_add'),
    path('cart/update/<uuid:pk>/', CartUpdateView.as_view(), name='cart_update'),
    path('cart/remove/<uuid:pk>/', CartRemoveView.as_view(), name='cart_remove'),
    
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
"""

files = {
    os.path.join(base_dir, "permissions.py"): permissions_code,
    os.path.join(base_dir, "serializers.py"): serializers_code,
    os.path.join(base_dir, "views.py"): views_code,
    os.path.join(base_dir, "urls.py"): urls_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Orders API files successfully created.")
