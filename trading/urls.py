from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='trading/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('history/', views.trade_history, name='trade_history'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)