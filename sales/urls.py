from django.urls import path, include
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.index, name="index"),
]
