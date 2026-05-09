import os

backend_dir = r"E:\project\shopconnect\apps\catalog"

# 1. Update serializers.py
with open(os.path.join(backend_dir, "serializers.py"), "a", encoding="utf-8") as f:
    f.write("\nfrom .models import Wishlist\n")
    f.write("""
class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details', 'created_at']
""")

# 2. Update views.py
with open(os.path.join(backend_dir, "views.py"), "a", encoding="utf-8") as f:
    f.write("\nfrom .models import Wishlist\n")
    f.write("from .serializers import WishlistSerializer\n")
    f.write("""
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
""")

# 3. Update urls.py
urls_path = os.path.join(backend_dir, "urls.py")
with open(urls_path, "r", encoding="utf-8") as f:
    urls_content = f.read()

urls_content = urls_content.replace(
    "from .views import CategoryListView, ProductListView, ProductDetailView, SellerProductListCreateView, SellerProductDetailView",
    "from .views import CategoryListView, ProductListView, ProductDetailView, SellerProductListCreateView, SellerProductDetailView, WishlistListView, WishlistAddView, WishlistRemoveView"
)

# Insert the new routes before seller endpoints
routes = """    
    # Wishlist endpoints
    path('wishlist/', WishlistListView.as_view(), name='wishlist_list'),
    path('wishlist/add/', WishlistAddView.as_view(), name='wishlist_add'),
    path('wishlist/remove/<uuid:product_id>/', WishlistRemoveView.as_view(), name='wishlist_remove'),
    
    # Seller endpoints"""
urls_content = urls_content.replace("    # Seller endpoints", routes)

with open(urls_path, "w", encoding="utf-8") as f:
    f.write(urls_content)

print("Backend wishlist endpoints created.")
