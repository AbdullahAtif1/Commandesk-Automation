from django.urls import path, include
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.index, name="index"),
]
