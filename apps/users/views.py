from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                "success": True,
                "data": {
                    "user": UserSerializer(user).data,
                    "tokens": tokens
                }
            }, status=status.HTTP_201_CREATED)
            
        field = next(iter(serializer.errors))
        error_message = serializer.errors[field][0]
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": error_message,
                "field": field
            }
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']
            user = authenticate(phone=phone, password=password)
            
            if user is not None:
                if not user.is_active:
                    return Response({
                        "success": False,
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "Ce compte a été désactivé."
                        }
                    }, status=status.HTTP_403_FORBIDDEN)
                    
                tokens = get_tokens_for_user(user)
                return Response({
                    "success": True,
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": tokens
                    }
                })
            
            return Response({
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Numéro de téléphone ou mot de passe incorrect."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        field = next(iter(serializer.errors))
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": serializer.errors[field][0],
                "field": field
            }
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # We catch the normal DRF SimpleJWT response and wrap it
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                "success": True,
                "data": response.data
            })
        return response # The custom exception handler will catch expired errors

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "success": True,
            "data": serializer.data
        })
# ----------- ADMIN ENDPOINTS -----------
from rest_framework import serializers, generics
from apps.users.models import User, Shop
from apps.logistics.permissions import IsAdmin
from apps.users.serializers import UserSerializer
from apps.catalog.pagination import StandardResultsSetPagination

class AdminShopSerializer(serializers.ModelSerializer):
    seller_phone = serializers.CharField(source='seller.user.phone', read_only=True)
    class Meta:
        model = Shop
        fields = ['id', 'name', 'slug', 'seller_phone', 'is_active', 'created_at']

class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = User.objects.filter(deleted_at__isnull=True).order_by('-created_at')
        role = self.request.query_params.get('role')
        status_val = self.request.query_params.get('status')
        if role: qs = qs.filter(role=role)
        if status_val: qs = qs.filter(is_active=(status_val == 'active'))
        return qs

class AdminUserStatusUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk, deleted_at__isnull=True)
            status_val = request.data.get('status') # 'active' or 'suspended'
            if status_val == 'active':
                user.is_active = True
            else:
                user.is_active = False
            user.save()
            return Response({"success": True, "data": {"is_active": user.is_active}})
        except User.DoesNotExist:
            return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Utilisateur introuvable"}}, status=404)

class AdminShopListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminShopSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Shop.objects.filter(deleted_at__isnull=True).order_by('-created_at')

class AdminShopVerifyView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk, deleted_at__isnull=True)
            status_val = request.data.get('status') # 'approved' or 'rejected'
            if status_val == 'approved':
                shop.is_active = True
                shop.seller.is_verified = True
                shop.seller.save()
            else:
                shop.is_active = False
                shop.seller.is_verified = False
                shop.seller.save()
            shop.save()
            return Response({"success": True, "data": {"is_active": shop.is_active}})
        except Shop.DoesNotExist:
            return Response({"success": False, "error": {"code": "NOT_FOUND", "message": "Boutique introuvable"}}, status=404)

# ----------- SELLER ENDPOINTS -----------
from django.db.models import Sum
from apps.orders.models import OrderProduct
from apps.catalog.permissions import IsSeller

class SellerStatsView(views.APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request):
        try:
            shop = request.user.seller_profile.shop
        except Exception:
            return Response({
                "success": False, 
                "error": {"code": "NO_SHOP", "message": "Boutique introuvable."}
            }, status=400)

        # Total Sales (Completed orders)
        total_sales = OrderProduct.objects.filter(
            shop=shop, 
            order__status='completed'
        ).aggregate(Sum('order_item__total_price'))['order_item__total_price__sum'] or 0
        
        # Total Orders (Distinct orders containing shop's products)
        total_orders = OrderProduct.objects.filter(shop=shop).values('order').distinct().count()
        
        # Total Products
        total_products = shop.products.filter(deleted_at__isnull=True).count()
        
        return Response({
            "success": True,
            "data": {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "total_products": total_products,
                "currency": "BIF"
            }
        })
