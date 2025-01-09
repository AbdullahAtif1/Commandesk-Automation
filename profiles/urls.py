from django.urls import path, include
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.client_management, name="client_management"),
]
