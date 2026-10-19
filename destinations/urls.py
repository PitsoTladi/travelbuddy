from .views import DestinationViewSets
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path
from .map_views import MapLocationsView
router = DefaultRouter()
router.register('destinations', DestinationViewSets)


urlpatterns = [
    path("map/locations/", MapLocationsView.as_view(), name="map-locations"),
]
urlpatterns +=  router.urls

