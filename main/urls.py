from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Existing routes
    path('', views.home, name='home'),
    path('api/login/', views.logPlantFeed, name='logPlantFeed'),
    path('api/logout/', views.logout, name='logout'),
    path('api/profile/', views.profile, name='profile'),

    # New JWT-based API endpoints for mobile login
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login endpoint
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token endpoint
]
