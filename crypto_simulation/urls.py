from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect root URL to API
    path('', RedirectView.as_view(url='/api/', permanent=False), name='index'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Trading API endpoints
    path('api/', include('trading.urls')),
    
    # DRF browsable API authentication
    path('api-auth/', include('rest_framework.urls')),
]