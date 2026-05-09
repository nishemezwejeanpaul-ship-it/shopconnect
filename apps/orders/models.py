import uuid
from django.db import models
from apps.users.models import BaseModel

class DeliveryMethod(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ShippingAddress(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='shipping_addresses')
    region = models.ForeignKey('logistics.Region', on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(max_length=50, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

class Cart(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    coupon_code = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('user', 'product', 'variant')

class Order(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey('catalog.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='BIF')
    final_delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_point = models.ForeignKey('logistics.PickupPoint', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        indexes = [models.Index(fields=['user', '-created_at'])]

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey('users.Shop', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['shop']),
        ]

class OrderProduct(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    shop = models.ForeignKey('users.Shop', on_delete=models.PROTECT)
    shipment = models.ForeignKey('logistics.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_products')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class Return(BaseModel):
    REASON_CHOICES = (
        ('damaged', 'Damaged'),
        ('wrong_item', 'Wrong Item'),
        ('not_as_described', 'Not As Described'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    refund_method = models.CharField(max_length=20, choices=(('original','Original'), ('wallet','Wallet'), ('credit','Credit')), null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class Dispute(BaseModel):
    TYPE_CHOICES = (
        ('non_delivery', 'Non Delivery'),
        ('fraud', 'Fraud'),
        ('quality', 'Quality'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('escalated', 'Escalated'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    raised_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='disputes_raised')
    against_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='disputes_against')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes_resolved')
    resolution_note = models.TextField(blank=True)
