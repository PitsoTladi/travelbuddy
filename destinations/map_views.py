
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

from destinations.models import Destination
from events.models import Event


class MapLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=["destination", "event"])
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    city = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class MapLocationsView(generics.GenericAPIView):
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
                "latitude": event.latitude,
                "longitude": event.longitude,
                "city": event.city,
                "description": event.description or "",
                "price": event.price,
            })

        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)
