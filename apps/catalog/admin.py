from django.contrib import admin
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
