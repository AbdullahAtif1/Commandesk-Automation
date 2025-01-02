from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Add fields to the user list display
    list_display = ('username', 'email', 'is_staff', 'is_active', 'phone_number', 'website')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

    # Customizing the user form in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('email', 'first_name', 'last_name', 'profile_picture', 'company_logo', 'website', 'store_location', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # Add fields to the subscription list display
    list_display = ('user', 'plan_name', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan_name', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__username', 'user__email', 'plan_name')
    ordering = ('-start_date',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_owner', 'name', 'email', 'client_type', 'total_spent', 'updated_at',)
    list_filter = ('company_owner', 'client_type',)
    ordering = ('-updated_at',)
