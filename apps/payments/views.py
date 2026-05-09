import uuid
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
                
                # Dynamic commission rates based on business model
                method_code = order.final_delivery_method.code if order.final_delivery_method else 'DOOR_FREE'
                rates = {
                    'DOOR_FREE': Decimal('0.07'),
                    'PICKUP_FREE': Decimal('0.06'),
                    'DOOR_EXPRESS': Decimal('0.05')
                }
                commission_rate = rates.get(method_code, Decimal('0.07'))

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
