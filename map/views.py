
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

from destinations.models import Destination
from events.models import Event
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class MapLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    address = serializers.CharField(allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True)
    city = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)




class MapLocationsView(generics.GenericAPIView):
    queryset = Destination.objects.none()
    permission_classes = [permissions.AllowAny]
    serializer_class = MapLocationSerializer

    def get(self, request, *args, **kwargs):
        locations = []

        destinations = Destination.objects.exclude(
            latitude__isnull=True
        ).exclude(
            longitude__isnull=True
        )

        for destination in destinations:
            locations.append({
                "id": destination.id,
                "name": destination.name,
                "type": "destination",
                "address": destination.address,
                "latitude": destination.latitude,
                "longitude": destination.longitude,
                "city": destination.city,
                "description": destination.description or "",
                "price": destination.price,
            })

        events = Event.objects.exclude(
            latitude__isnull=True
        ).exclude(
            longitude__isnull=True
        )

        for event in events:
            locations.append({
                "id": event.id,
                "name": event.name,
                "type": "event",
                "address": event.address,
                "latitude": event.latitude,
                "longitude": event.longitude,
                "city": event.city,
                "description": event.description or "",
                "price": event.price,
            })

        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)

class AddressSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) < 5 or len(query) > 255:
            return Response(
                {"error": "Enter an address between 5 and 255 characters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = "travelbuddy_address_" + query.lower()
        results = cache.get(cache_key)

        if results is None:
            # Allow no more than one uncached request per second.
            if not cache.add("travelbuddy_nominatim_limit", True, 1):
                return Response(
                    {"error": "Please wait a moment before searching again."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            params = urlencode({
                "q": query,
                "format": "jsonv2",
                "limit": 5,
                "countrycodes": "za",
                "addressdetails": 1,
            })

            url = (
                "https://nominatim.openstreetmap.org/search?"
                + params
            )

            req = Request(
                url,
                headers={
                    "User-Agent": "TravelBuddySA/1.0 (student project)"
                }
            )

            try:
                with urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))

                results = []

                for item in data:
                    results.append({
                        "place_id": item.get("place_id"),
                        "address": item.get("display_name", ""),
                        "latitude": item.get("lat"),
                        "longitude": item.get("lon"),
                    })

                cache.set(cache_key, results, 86400)

            except (HTTPError, URLError, TimeoutError, ValueError):
                return Response(
                    {"error": "Address search is temporarily unavailable."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        return Response({"results": results})
