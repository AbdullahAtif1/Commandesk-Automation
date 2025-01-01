from django.contrib import admin
from .models import *


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'name', 'address', 'contact_number')
    list_filter = ('company_owner',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'name', 'contact_details', 'email')
    list_filter = ('company_owner',)



class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'name', 'sku', 'price', 'category', 'is_active')
    list_filter = ('company_owner', 'category',)  # To filter products by category
    filter_horizontal = ('batches',)  # Enables a multi-select widget for batches
    inlines = [ProductVariationInline]


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'batch_number', 'supplier', 'manufacture_date', 'expiry_date')
    list_filter = ('company_owner', 'supplier', 'manufacture_date', 'expiry_date')  # Filters for better management
    


class InventoryLogInline(admin.StackedInline):  # StackedInline for detailed display
    model = InventoryLog
    extra = 1

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'product_variation', 'batch', 'warehouse', 'quantity')
    inlines = [InventoryLogInline]
    list_filter = ('company_owner',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'name', 'description', 'created_at')
    list_filter = ('company_owner',)



