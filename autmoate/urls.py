from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# update later to add the company name before the url and after the domain name

urlpatterns = [
    path('admin/', admin.site.urls),
		path('', include('main.urls')),
		path('dashboard/', include('dashboard.urls')),
		path('inventory-tracking/', include('stock_track.urls')),
		path('sales/', include('sales.urls')),
		path('profile/', include('profiles.urls')),
    path('accounts/', include('allauth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

