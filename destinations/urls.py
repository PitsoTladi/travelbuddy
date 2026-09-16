from .views import DestinationViewSets
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('destinations', DestinationViewSets)

urlpatterns =  router.urls


