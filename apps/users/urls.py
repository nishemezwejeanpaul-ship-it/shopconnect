from django.urls import path
from .views import RegisterView, LoginView, CustomTokenRefreshView, UserProfileView
from .views import AdminUserListView, AdminUserStatusUpdateView, AdminShopListView, AdminShopVerifyView, SellerStatsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='me'),
    
    # Admin Endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<uuid:pk>/status/', AdminUserStatusUpdateView.as_view(), name='admin_user_status_update'),
    path('admin/shops/', AdminShopListView.as_view(), name='admin_shop_list'),
    path('admin/shops/<uuid:pk>/verify/', AdminShopVerifyView.as_view(), name='admin_shop_verify'),

    # Seller Endpoints
    path('seller/stats/', SellerStatsView.as_view(), name='seller_stats'),
]
