from django.urls import path
from .views import (
    CartListView, CartAddView, CartUpdateView, CartRemoveView,
    OrderCreateView, OrderListView, OrderDetailView,
    SellerOrderListView, SellerOrderStatusUpdateView,
    OrderTrackingView, ShippingCalculationView,
    DeliveryMethodListView, ShippingAddressListCreateView
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
    path('orders/calculate-shipping/', ShippingCalculationView.as_view(), name='calculate_shipping'),
    path('delivery-methods/', DeliveryMethodListView.as_view(), name='delivery_method_list'),
    path('shipping-addresses/', ShippingAddressListCreateView.as_view(), name='shipping_address_list_create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),

    # Orders Seller
    path('seller/orders/', SellerOrderListView.as_view(), name='seller_order_list'),
    path('seller/orders/<uuid:pk>/status/', SellerOrderStatusUpdateView.as_view(), name='seller_order_status_update'),

    # Tracking
    path('orders/<uuid:pk>/tracking/', OrderTrackingView.as_view(), name='order_tracking'),
]
