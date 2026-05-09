from rest_framework import generics, status, views
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

    def get(self, request):
        try:
            shop = request.user.seller_profile.shop
            products = Product.objects.filter(shop=shop, deleted_at__isnull=True).prefetch_related('images')
            serializer = ProductListSerializer(products, many=True)
            return Response({
                "success": True,
                "data": serializer.data
            })
        except Exception:
            return Response({
                "success": False,
                "error": {"code": "NO_SHOP", "message": "Boutique introuvable."}
            }, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Produit introuvable."
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductDetailSerializer(product)
        return Response({
            "success": True,
            "data": serializer.data
        })

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

from .models import Wishlist
from .serializers import WishlistSerializer

class WishlistListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Wishlist.objects.select_related(
            'product', 'product__shop', 'product__category'
        ).prefetch_related('product__images').filter(
            user=self.request.user,
            deleted_at__isnull=True
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class WishlistAddView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"success": False, "error": {"code": "MISSING_PRODUCT", "message": "product_id requis"}}, status=400)
            
        try:
            product = Product.objects.get(id=product_id, deleted_at__isnull=True)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            return Response({"success": True, "data": WishlistSerializer(wishlist_item).data}, status=201 if created else 200)
        except Product.DoesNotExist:
            return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Produit introuvable"}}, status=404)

class WishlistRemoveView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        deleted, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        if deleted:
            return Response({"success": True, "data": None}, status=200)
        return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Produit non trouvé dans la liste de souhaits"}}, status=404)
