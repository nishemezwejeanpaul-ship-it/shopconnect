from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Seller, Shop, Message, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'deleted_at')
    search_fields = ('phone', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    filter_horizontal = ()
    list_filter = ('role', 'is_staff', 'is_active', ('deleted_at', admin.EmptyFieldListFilter))
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'deleted_at')}),
    )
    
    def get_queryset(self, request):
        # Admin should see soft-deleted users as well to manage them
        return self.model.all_objects.get_queryset()

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'created_at', 'deleted_at')
    list_filter = ('is_verified', ('deleted_at', admin.EmptyFieldListFilter))
    search_fields = ('user__phone', 'national_id', 'business_registration_number')
    
    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'is_active', 'created_at', 'deleted_at')
    list_filter = ('is_active', ('deleted_at', admin.EmptyFieldListFilter))
    search_fields = ('name', 'seller__user__phone')
    
    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'status', 'created_at')
    list_filter = ('status', 'type')
