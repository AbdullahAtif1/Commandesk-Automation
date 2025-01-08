from django.urls import path, include
from . import views

app_name = 'stock_track'

urlpatterns = [
    path('', views.index, name="index"),

		# Btach
		path("batches/", views.batch_list, name="batch_list"),
    path("batches/create/", views.create_batch, name="create_batch"),
    path("batches/<int:id>/update/", views.update_batch, name="update_batch"),
    path("batches/<int:id>/delete/", views.delete_batch, name="delete_batch"),

		# Category
		path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:id>/update/', views.update_category, name='update_category'),
    path('categories/<int:id>/delete/', views.delete_category, name='delete_category'),

		# Supply
		path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.create_supplier, name='create_supplier'),
    path('suppliers/<int:id>/update/', views.update_supplier, name='update_supplier'),
    path('suppliers/<int:id>/delete/', views.delete_supplier, name='delete_supplier'),

		# Warehouse
		path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.create_warehouse, name='create_warehouse'),
    path('warehouses/<int:id>/update/', views.update_warehouse, name='update_warehouse'),
    path('warehouses/<int:id>/delete/', views.delete_warehouse, name='delete_warehouse'),

		# Product
		path('products/', views.product_list, name='product_list'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<int:id>/update/', views.update_product, name='update_product'),
    path('products/<int:id>/delete/', views.delete_product, name='delete_product'),

]
