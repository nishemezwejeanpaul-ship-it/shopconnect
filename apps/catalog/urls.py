from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView, SellerProductListCreateView, SellerProductDetailView, WishlistListView, WishlistAddView, WishlistRemoveView

urlpatterns = [
    # Public endpoints
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
    
    
    # Wishlist endpoints
    path('wishlist/', WishlistListView.as_view(), name='wishlist_list'),
    path('wishlist/add/', WishlistAddView.as_view(), name='wishlist_add'),
    path('wishlist/remove/<uuid:product_id>/', WishlistRemoveView.as_view(), name='wishlist_remove'),
    
    # Seller endpoints
    path('seller/products/', SellerProductListCreateView.as_view(), name='seller_product_list_create'),
    path('seller/products/<uuid:pk>/', SellerProductDetailView.as_view(), name='seller_product_detail'),
]
