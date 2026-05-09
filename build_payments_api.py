import os

base_dir_payments = r"E:\project\shopconnect\apps\payments"
base_dir_orders = r"E:\project\shopconnect\apps\orders"

# ---------------- PAYMENTS API ----------------

payments_permissions_code = """from rest_framework.permissions import BasePermission

class IsOrderOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
"""

payments_serializers_code = """from rest_framework import serializers
from .models import Payment, Transaction
from apps.orders.models import Order

class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'currency', 'method', 'status', 'external_reference', 'paid_at', 'created_at']

class CallbackSerializer(serializers.Serializer):
    external_reference = serializers.CharField(required=True)
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)
"""

payments_views_code = """import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Payment, Transaction
from apps.orders.models import Order, OrderItem
from .serializers import PaymentInitiateSerializer, PaymentSerializer, CallbackSerializer

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

class PaymentInitiateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            method = serializer.validated_data['method']

            try:
                order = Order.objects.get(id=order_id, user=request.user, deleted_at__isnull=True)
            except Order.DoesNotExist:
                return error_response("NOT_FOUND", "Commande introuvable.", status.HTTP_404_NOT_FOUND)

            if hasattr(order, 'payment') and order.payment.status == 'paid':
                return error_response("ALREADY_PAID", "Cette commande a déjà été payée.")

            # Generate mock external reference for mobile money polling
            ext_ref = f"MM-{uuid.uuid4().hex[:10].upper()}"

            payment, created = Payment.objects.update_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'amount': order.total_amount,
                    'currency': order.currency,
                    'method': method,
                    'status': 'pending',
                    'external_reference': ext_ref
                }
            )

            return success_response({
                "payment_id": payment.id,
                "external_reference": payment.external_reference,
                "status": payment.status
            }, status.HTTP_201_CREATED)

        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])

class PaymentCallbackView(views.APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        secret = request.headers.get('X-Callback-Secret')
        if secret != settings.MOBILE_MONEY_CALLBACK_SECRET:
            return error_response("UNAUTHORIZED", "Secret invalide.", status.HTTP_401_UNAUTHORIZED)

        serializer = CallbackSerializer(data=request.data)
        if serializer.is_valid():
            ext_ref = serializer.validated_data['external_reference']
            new_status = serializer.validated_data['status']

            try:
                payment = Payment.objects.select_for_update().get(external_reference=ext_ref)
            except Payment.DoesNotExist:
                return error_response("NOT_FOUND", "Paiement introuvable.", status.HTTP_404_NOT_FOUND)

            if payment.status == 'paid':
                return success_response({"message": "Paiement déjà traité."})

            payment.status = new_status
            if new_status == 'paid':
                payment.paid_at = timezone.now()
                
                # Update order status
                order = payment.order
                order.status = 'confirmed'
                order.save()

                # Generate Transactions for each OrderItem
                items = OrderItem.objects.filter(order=order)
                commission_rate = Decimal('0.05')

                for item in items:
                    gross_amount = item.total_price
                    commission = gross_amount * commission_rate
                    net_amount = gross_amount - commission

                    Transaction.objects.create(
                        payment=payment,
                        order_item=item,
                        shop=item.shop,
                        gross_amount=gross_amount,
                        commission_rate=commission_rate,
                        commission=commission,
                        net_amount=net_amount,
                        status='pending' # pending until payout
                    )

            payment.save()
            return success_response({"message": "Callback traité avec succès."})

        field = next(iter(serializer.errors))
        return error_response("VALIDATION_ERROR", serializer.errors[field][0])

class PaymentStatusView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, deleted_at__isnull=True)
            payment = order.payment
            return success_response(PaymentSerializer(payment).data)
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return error_response("NOT_FOUND", "Paiement introuvable.", status.HTTP_404_NOT_FOUND)
"""

payments_urls_code = """from django.urls import path
from .views import PaymentInitiateView, PaymentCallbackView, PaymentStatusView

urlpatterns = [
    path('initiate/', PaymentInitiateView.as_view(), name='payment_initiate'),
    path('callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path('status/<uuid:order_id>/', PaymentStatusView.as_view(), name='payment_status'),
]
"""

# ---------------- SELLER ORDERS API ----------------

orders_urls_code = """from django.urls import path
from .views import (
    CartListView, CartAddView, CartUpdateView, CartRemoveView,
    OrderCreateView, OrderListView, OrderDetailView,
    SellerOrderListView, SellerOrderStatusUpdateView
)

urlpatterns = [
    # Cart Public
    path('cart/', CartListView.as_view(), name='cart_list'),
    path('cart/add/', CartAddView.as_view(), name='cart_add'),
    path('cart/update/<uuid:pk>/', CartUpdateView.as_view(), name='cart_update'),
    path('cart/remove/<uuid:pk>/', CartRemoveView.as_view(), name='cart_remove'),
    
    # Orders Public
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),

    # Orders Seller
    path('seller/orders/', SellerOrderListView.as_view(), name='seller_order_list'),
    path('seller/orders/<uuid:pk>/status/', SellerOrderStatusUpdateView.as_view(), name='seller_order_status_update'),
]
"""

import sys
# The rest of apps/orders/views.py additions:
orders_views_additions = """
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
"""

def append_to_file(filepath, content):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

# Files creation
files = {
    os.path.join(base_dir_payments, "permissions.py"): payments_permissions_code,
    os.path.join(base_dir_payments, "serializers.py"): payments_serializers_code,
    os.path.join(base_dir_payments, "views.py"): payments_views_code,
    os.path.join(base_dir_payments, "urls.py"): payments_urls_code,
    os.path.join(base_dir_orders, "urls.py"): orders_urls_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

append_to_file(os.path.join(base_dir_orders, "views.py"), orders_views_additions)

print("Payments API files and Seller Order routes successfully created.")
