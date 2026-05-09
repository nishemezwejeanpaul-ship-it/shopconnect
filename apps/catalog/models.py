import uuid
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
