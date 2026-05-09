from rest_framework import serializers
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

from .models import Wishlist

class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details', 'created_at']
