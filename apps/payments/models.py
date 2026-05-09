import uuid
from django.db import models
from apps.users.models import BaseModel

class Payment(BaseModel):
    METHOD_CHOICES = (
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    provider = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_reference = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

class Transaction(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('paid_out', 'Paid Out'),
    )
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE)
    shop = models.ForeignKey('users.Shop', on_delete=models.CASCADE, related_name='transactions')
    gross_amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4)
    commission = models.DecimalField(max_digits=15, decimal_places=2)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class SellerPayout(BaseModel):
    METHOD_CHOICES = (
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    seller = models.ForeignKey('users.Seller', on_delete=models.CASCADE, related_name='payouts')
    batch_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    period_from = models.DateField()
    period_to = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
