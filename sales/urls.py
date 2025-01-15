from django.urls import path, include
from . import views

app_name = 'sales'

urlpatterns = [
		# Coupons
		path("coupons/", views.manage_coupons, name="manage_coupons"),
		path("coupons/update/<int:coupon_id>/", views.update_coupon, name="update_coupon"),
    path("coupons/delete/<int:coupon_id>/", views.delete_coupon, name="delete_coupon"),

		# Sales
		path("add/", views.add_sale, name="add"),
		path("", views.sales_list, name="list"),
    path("delete/<int:sale_id>/", views.delete_sale, name="delete"),
		path("edit/<int:sale_id>/", views.edit_sale, name="edit_sale"),
]
