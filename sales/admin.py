from django.contrib import admin
from .models import *


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('company_owner','code', 'discount_percentage', 'active', 'expiry_date')
    list_filter = ('company_owner', 'active', 'expiry_date')
    search_fields = ('company_owner', 'code',)
    ordering = ('expiry_date',)
    

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1  # Number of empty forms to display
    readonly_fields = ['unit_price', 'total_price']  # Fields that should be read-only in the inline form

@admin.register(Sale)  # Using the decorator to register Sale with the admin
class SaleAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'client', 'total_price', 'sale_time', 'company_owner')
    search_fields = ('company_owner', 'client__name', 'company_owner__username')
    list_filter = ('company_owner', 'sale_time', 'company_owner', 'client')
    inlines = [SaleItemInline]  # Register the SaleItemInline in the SaleAdmin


