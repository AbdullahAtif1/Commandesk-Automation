from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name="index"),
		path("complaints/", views.complaint_list, name="complaint_list"),
    path("complaints/edit/<int:id>/", views.edit_complaint, name="edit_complaint"),
    path("complaints/delete/<int:id>/", views.delete_complaint, name="delete_complaint"),
		path('complaints/<int:id>/', views.complaint_detail, name='complaint_detail')
]
