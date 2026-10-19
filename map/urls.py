from .views import MapLocationsView
from django.urls import path


urlpatterns = [
    path("map/locations/", MapLocationsView.as_view(), name="map-locations"),
]
