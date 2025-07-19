from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User, Client, Product, ProductVariant,
    Cart, CartItem, PurchaseOrder, OrderItem
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'role')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('name', 'role', 'created_at')}),
    )
    readonly_fields = ('created_at',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'tax_id', 'phone', 'email', 'user')
    search_fields = ('company_name', 'tax_id', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'is_active')
    list_filter = ('brand', 'category', 'is_active')
    search_fields = ('name', 'brand', 'category')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'stock', 'unit_price', 'bulk_price')
    list_filter = ('color', 'size', 'is_luminous')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'variant', 'quantity')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('client__company_name',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'variant', 'quantity', 'unit_price', 'subtotal')
