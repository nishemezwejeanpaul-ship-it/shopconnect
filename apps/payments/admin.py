from django.contrib import admin
from .models import Payment, Transaction, SellerPayout

admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(SellerPayout)
