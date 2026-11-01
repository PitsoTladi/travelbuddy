
from django.urls import path
from .views import MapLocationsView, AddressSearchView


urlpatterns = [
    path("map/locations/", MapLocationsView.as_view(), name="map-locations"),
    path("address-search/",AddressSearchView.as_view(),name="address-search"
    ),
]
