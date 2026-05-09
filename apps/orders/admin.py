from django.contrib import admin
from .models import DeliveryMethod, ShippingAddress, Cart, Order, OrderItem, OrderProduct, Return, Dispute

admin.site.register(DeliveryMethod)
admin.site.register(ShippingAddress)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderProduct)
admin.site.register(Return)
admin.site.register(Dispute)
