from django.urls import path
from .views import PaymentInitiateView, PaymentCallbackView, PaymentStatusView

urlpatterns = [
    path('initiate/', PaymentInitiateView.as_view(), name='payment_initiate'),
    path('callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path('status/<uuid:order_id>/', PaymentStatusView.as_view(), name='payment_status'),
]
