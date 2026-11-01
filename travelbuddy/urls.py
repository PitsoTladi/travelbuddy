from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User registration and user endpoints
    path('api/', include('users.urls')),

    # Application endpoints
    path('api/', include('destinations.urls')),
    path('api/', include('map.urls')),
    path('api/', include('events.urls')),
    path('api/', include('interests.urls')),
    path('api/', include('posts.urls')),
    path('api/', include('reviews.urls')),
    path('api/', include('recommendations.urls')),
    path('api/', include('chatbot.urls')),
]