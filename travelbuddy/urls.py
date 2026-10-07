"""
URL configuration for travelbuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView
from users.views import userViewSet, register





urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('destinations.urls')),
    path('api/', include('events.urls')),
    path('api/', include('interests.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name= 'token_obtain_pair' ),
    path('api/refresh',TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', register, name='register' ),
    path('api/', include('posts.urls')),
    path('api/', include('reviews.urls'))
]

