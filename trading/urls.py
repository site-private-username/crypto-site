from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'chart-types', views.ChartTypeViewSet, basename='chart-type')
router.register(r'candles', views.CandleViewSet, basename='candle')
router.register(r'bets', views.BetViewSet, basename='bet')
router.register(r'manual-controls', views.ManualControlViewSet, basename='manual-control')

router.register(r'completed-bets', views.CompletedBetViewSet, basename='completed-bet')

urlpatterns = [
    # API root
    path('', views.api_root, name='api-root'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Auth endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]