from rest_framework import serializers
from .models import Cart, Order, OrderItem, OrderProduct, DeliveryMethod, ShippingAddress
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
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'variant', 'shop', 'quantity', 'unit_price', 'total_price']

class ShippingAddressSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = ShippingAddress
        fields = ['id', 'region', 'region_name', 'label', 'address', 'phone', 'is_default']
        read_only_fields = ['id']

class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'code', 'name', 'description']

from apps.payments.serializers import PaymentSerializer
from apps.logistics.serializers import PickupPointSerializer

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address_details = ShippingAddressSerializer(source='shipping_address', read_only=True)
    pickup_point_details = PickupPointSerializer(source='pickup_point', read_only=True)
    payment_details = PaymentSerializer(source='payment', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'subtotal', 'shipping_fee', 'discount_amount', 'total_amount', 'currency', 
            'status', 'final_delivery_method', 'pickup_point', 'pickup_point_details',
            'shipping_address', 'shipping_address_details', 'payment_details',
            'created_at', 'items'
        ]
