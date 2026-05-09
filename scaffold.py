import os

base_dir = r"E:\project\shopconnect\apps"

# ----------------- LOGISTICS -----------------
logistics_models = """import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import BaseModel

class Region(BaseModel):
    TYPE_CHOICES = (
        ('province', 'Province'),
        ('city', 'City'),
        ('zone', 'Zone'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_regions')

    def __str__(self):
        return self.name

class HubLocation(BaseModel):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PickupPoint(BaseModel):
    TYPE_CHOICES = (
        ('shop', 'Shop'),
        ('partner', 'Partner'),
        ('locker', 'Locker'),
    )
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DeliveryAgent(BaseModel):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('on_delivery', 'On Delivery'),
        ('offline', 'Offline'),
    )
    VEHICLE_CHOICES = (
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('van', 'Van'),
    )
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='delivery_agent_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, null=True, blank=True)
    license_plate = models.CharField(max_length=30, blank=True)
    hub = models.ForeignKey(HubLocation, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Driver: {self.user.phone}"

class ShippingRule(BaseModel):
    from_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='rules_from')
    to_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='rules_to')
    delivery_method = models.ForeignKey('orders.DeliveryMethod', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    estimated_days = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='BIF')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('from_region', 'to_region', 'delivery_method')

    def __str__(self):
        return f"{self.from_region} -> {self.to_region}"

class Shipment(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    hub_from = models.ForeignKey(HubLocation, on_delete=models.PROTECT, related_name='shipments_origin')
    hub_to = models.ForeignKey(HubLocation, on_delete=models.PROTECT, related_name='shipments_dest')
    driver = models.ForeignKey(DeliveryAgent, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Shipment {self.id}"

class ShipmentItem(BaseModel):
    STATUS_CHOICES = (
        ('packed', 'Packed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('lost', 'Lost'),
    )
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    order_product = models.ForeignKey('orders.OrderProduct', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='packed')

    class Meta:
        unique_together = ('shipment', 'order_product')

class ShipmentTracking(BaseModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    recorded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
"""

logistics_admin = """from django.contrib import admin
from .models import Region, HubLocation, PickupPoint, DeliveryAgent, ShippingRule, Shipment, ShipmentItem, ShipmentTracking

admin.site.register(Region)
admin.site.register(HubLocation)
admin.site.register(PickupPoint)
admin.site.register(DeliveryAgent)
admin.site.register(ShippingRule)
admin.site.register(Shipment)
admin.site.register(ShipmentItem)
admin.site.register(ShipmentTracking)
"""

# ----------------- CATALOG -----------------
catalog_models = """import uuid
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from apps.users.models import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    photo_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Product(BaseModel):
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    )
    shop = models.ForeignKey('users.Shop', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    discount_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    class Meta:
        unique_together = ('shop', 'slug')
        indexes = [
            models.Index(fields=['shop', 'status']),
            models.Index(fields=['category']),
            GinIndex(fields=['name'], name='idx_products_name_trgm', opclasses=['gin_trgm_ops']),
        ]

    def __str__(self):
        return self.name

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    is_main = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    additional_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)

class ProductTag(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)

    class Meta:
        unique_together = ('product', 'tag')
        indexes = [models.Index(fields=['tag'])]

class Discount(BaseModel):
    TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='discounts')
    shop = models.ForeignKey('users.Shop', on_delete=models.CASCADE, null=True, blank=True, related_name='discounts')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class Coupon(BaseModel):
    TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
        ('free_shipping', 'Free Shipping'),
    )
    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    shop = models.ForeignKey('users.Shop', on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['code'])]

class Wishlist(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

class Review(BaseModel):
    REVIEW_TYPE_CHOICES = (
        ('product', 'Product'),
        ('shop', 'Shop'),
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPE_CHOICES)
    target_id = models.UUIDField()
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.SmallIntegerField()
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['review_type', 'target_id'])]
"""

catalog_admin = """from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, ProductTag, Discount, Coupon, Wishlist, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(ProductTag)
admin.site.register(Discount)
admin.site.register(Coupon)
admin.site.register(Wishlist)
admin.site.register(Review)
"""

# ----------------- ORDERS -----------------
orders_models = """import uuid
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
    currency = models.CharField(max_length=3, default='BIF')
    final_delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, blank=True)
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
"""

orders_admin = """from django.contrib import admin
from .models import DeliveryMethod, ShippingAddress, Cart, Order, OrderItem, OrderProduct, Return, Dispute

admin.site.register(DeliveryMethod)
admin.site.register(ShippingAddress)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderProduct)
admin.site.register(Return)
admin.site.register(Dispute)
"""

# ----------------- PAYMENTS -----------------
payments_models = """import uuid
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
"""

payments_admin = """from django.contrib import admin
from .models import Payment, Transaction, SellerPayout

admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(SellerPayout)
"""

# Write files
files = {
    os.path.join(base_dir, "logistics", "models.py"): logistics_models,
    os.path.join(base_dir, "logistics", "admin.py"): logistics_admin,
    os.path.join(base_dir, "catalog", "models.py"): catalog_models,
    os.path.join(base_dir, "catalog", "admin.py"): catalog_admin,
    os.path.join(base_dir, "orders", "models.py"): orders_models,
    os.path.join(base_dir, "orders", "admin.py"): orders_admin,
    os.path.join(base_dir, "payments", "models.py"): payments_models,
    os.path.join(base_dir, "payments", "admin.py"): payments_admin,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolded all models and admins.")
