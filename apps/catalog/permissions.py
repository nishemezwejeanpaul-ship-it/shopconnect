from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'seller')

class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return obj.shop == request.user.seller_profile.shop
        except Exception:
            return False
