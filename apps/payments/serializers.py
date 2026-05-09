from rest_framework import serializers
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
