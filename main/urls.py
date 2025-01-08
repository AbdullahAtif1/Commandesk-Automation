from django.urls import path, include
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name="index"),
		path('logout/', views.logout_view, name="logout"),
		path('pricing/', views.pricing, name="pricing_page"),
		path('about/', views.about, name="about_page"),
		path('contact/', views.contact, name="contact_page"),
]
