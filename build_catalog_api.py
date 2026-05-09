import os

base_dir = r"E:\project\shopconnect\apps\catalog"

permissions_code = """from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'seller')

class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return obj.shop == request.user.seller_profile.shop
        except Exception:
            return False
"""

pagination_code = """from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })
"""

serializers_code = """from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'photo_url', 'sort_order']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main', 'sort_order']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'value', 'additional_price', 'stock_quantity', 'sku']

class ProductListSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'discount_price', 'currency', 'stock_quantity', 'condition', 'shop_name', 'category_name', 'main_image']

    def get_main_image(self, obj):
        # Because we'll prefetch images, we can filter in python to avoid N+1
        images = obj.images.all()
        for img in images:
            if img.is_main:
                return img.image_url
        if images:
            return images[0].image_url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'discount_price', 'currency', 'stock_quantity', 'condition', 'status', 'shop', 'shop_name', 'category', 'category_name', 'images', 'variants', 'created_at']

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'discount_price', 'currency', 'stock_quantity', 'condition', 'status']
"""

views_code = """from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer
from .pagination import StandardResultsSetPagination
from .permissions import IsSeller, IsShopOwner

class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(deleted_at__isnull=True).order_by('sort_order', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Product.objects.select_related('shop', 'category').prefetch_related('images').filter(
            deleted_at__isnull=True, 
            status='active'
        )
        
        category = self.request.query_params.get('category')
        shop = self.request.query_params.get('shop')
        search = self.request.query_params.get('search')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category:
            qs = qs.filter(category_id=category)
        if shop:
            qs = qs.filter(shop_id=shop)
        if search:
            # Basic fallback if pg_trgm fails, but since we have it, we can use __icontains which utilizes it
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
            
        return qs.order_by('-created_at')

class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return Product.objects.select_related('shop', 'category').prefetch_related('images', 'variants').filter(
            deleted_at__isnull=True,
            status='active'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

class SellerProductListCreateView(views.APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    def post(self, request):
        try:
            shop = request.user.seller_profile.shop
        except Exception:
            return Response({
                "success": False,
                "error": {
                    "code": "NO_SHOP",
                    "message": "Vous devez avoir une boutique pour créer un produit."
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(shop=shop)
            return Response({
                "success": True,
                "data": ProductDetailSerializer(product).data
            }, status=status.HTTP_201_CREATED)
            
        field = next(iter(serializer.errors))
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": serializer.errors[field][0],
                "field": field
            }
        }, status=status.HTTP_400_BAD_REQUEST)

class SellerProductDetailView(views.APIView):
    permission_classes = [IsAuthenticated, IsSeller, IsShopOwner]

    def get_object(self, pk):
        try:
            obj = Product.objects.get(pk=pk, deleted_at__isnull=True)
            self.check_object_permissions(self.request, obj)
            return obj
        except Product.DoesNotExist:
            return None

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Produit introuvable."
                }
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            return Response({
                "success": True,
                "data": ProductDetailSerializer(updated_product).data
            })

        field = next(iter(serializer.errors))
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": serializer.errors[field][0],
                "field": field
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Produit introuvable."
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete logic requested
        product.deleted_at = timezone.now()
        product.status = 'archived'
        product.save()

        return Response({
            "success": True,
            "data": None
        }, status=status.HTTP_200_OK)
"""

urls_code = """from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView, SellerProductListCreateView, SellerProductDetailView

urlpatterns = [
    # Public endpoints
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Seller endpoints
    path('seller/products/', SellerProductListCreateView.as_view(), name='seller_product_list_create'),
    path('seller/products/<uuid:pk>/', SellerProductDetailView.as_view(), name='seller_product_detail'),
]
"""

files = {
    os.path.join(base_dir, "permissions.py"): permissions_code,
    os.path.join(base_dir, "pagination.py"): pagination_code,
    os.path.join(base_dir, "serializers.py"): serializers_code,
    os.path.join(base_dir, "views.py"): views_code,
    os.path.join(base_dir, "urls.py"): urls_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Catalog API files successfully created.")
