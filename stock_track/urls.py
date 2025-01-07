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

		
]
