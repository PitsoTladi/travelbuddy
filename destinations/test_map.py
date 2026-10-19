
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from events.models import Event
from interests.models import Interest
from users.models import User


class MapLocationsAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("map-locations")

        self.interest = Interest.objects.create(name="Adventure")

        self.user = User.objects.create_user(
            username="maptestuser",
            email="maptest@example.com",
            password="TestPassword123!",
        )

    def test_endpoint_is_accessible_without_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_destination_with_coordinates(self):
        Destination.objects.create(
            name="Magaliesburg",
            created_by=self.user,
            interest=self.interest,
            latitude=Decimal("-25.936700"),
            longitude=Decimal("27.906600"),
            price=Decimal("100.00"),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Magaliesburg")
        self.assertEqual(response.data[0]["type"], "destination")

    def test_returns_event_with_coordinates(self):
        event = Event.objects.create(
            name="Adventure Festival",
            created_by=self.user,
            latitude=Decimal("-26.204100"),
            longitude=Decimal("28.047300"),
            price=Decimal("50.00"),
        )
        event.interest.add(self.interest)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Adventure Festival")
        self.assertEqual(response.data[0]["type"], "event")

    def test_returns_destinations_and_events_together(self):
        Destination.objects.create(
            name="Magaliesburg",
            created_by=self.user,
            interest=self.interest,
            latitude=Decimal("-25.936700"),
            longitude=Decimal("27.906600"),
        )

        event = Event.objects.create(
            name="Adventure Festival",
            created_by=self.user,
            latitude=Decimal("-26.204100"),
            longitude=Decimal("28.047300"),
        )
        event.interest.add(self.interest)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            {item["type"] for item in response.data},
            {"destination", "event"},
        )

    def test_excludes_destination_without_coordinates(self):
        Destination.objects.create(
            name="Unmapped Destination",
            created_by=self.user,
            interest=self.interest,
            latitude=None,
            longitude=Decimal("27.906600"),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_excludes_event_without_coordinates(self):
        event = Event.objects.create(
            name="Unmapped Event",
            created_by=self.user,
            latitude=Decimal("-26.204100"),
            longitude=None,
        )
        event.interest.add(self.interest)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
