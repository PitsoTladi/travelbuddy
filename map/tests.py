from django.test import TestCase

# Create your tests here.

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from destinations.models import Destination
from events.models import Event
from interests.models import Interest


class MapLocationsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.interest = Interest.objects.create(name="Adventure")

    def test_endpoint_is_public(self):
        response = self.client.get("/api/map/locations/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_destination_with_coordinates_is_returned(self):
        destination = Destination.objects.create(
            name="Test Destination",
            description="A test destination",
            price=Decimal("150.00"),
            interest=self.interest,
            latitude=Decimal("-26.204100"),
            longitude=Decimal("28.047300"),
            city="Johannesburg",
        )

        response = self.client.get("/api/map/locations/")

        self.assertEqual(response.status_code, 200)
        location = next(
            item for item in response.data
            if item["id"] == destination.id
            and item["type"] == "destination"
        )

        self.assertEqual(location["name"], "Test Destination")
        self.assertEqual(location["latitude"], "-26.204100")
        self.assertEqual(location["longitude"], "28.047300")
        self.assertEqual(location["city"], "Johannesburg")
        self.assertEqual(location["description"], "A test destination")
        self.assertEqual(location["price"], "150.00")

    def test_event_with_coordinates_is_returned(self):
        event = Event.objects.create(
            name="Test Event",
            description="A test event",
            price=Decimal("75.00"),
            latitude=Decimal("-26.100000"),
            longitude=Decimal("28.100000"),
            city="Benoni",
        )

        response = self.client.get("/api/map/locations/")

        self.assertEqual(response.status_code, 200)
        location = next(
            item for item in response.data
            if item["id"] == event.id
            and item["type"] == "event"
        )

        self.assertEqual(location["name"], "Test Event")
        self.assertEqual(location["latitude"], "-26.100000")
        self.assertEqual(location["longitude"], "28.100000")
        self.assertEqual(location["city"], "Benoni")
        self.assertEqual(location["price"], "75.00")

    def test_destination_missing_latitude_is_excluded(self):
        destination = Destination.objects.create(
            name="Missing Latitude",
            interest=self.interest,
            latitude=None,
            longitude=Decimal("28.047300"),
        )

        response = self.client.get("/api/map/locations/")

        returned_ids = {
            (item["id"], item["type"]) for item in response.data
        }
        self.assertNotIn((destination.id, "destination"), returned_ids)

    def test_event_missing_longitude_is_excluded(self):
        event = Event.objects.create(
            name="Missing Longitude",
            latitude=Decimal("-26.100000"),
            longitude=None,
        )

        response = self.client.get("/api/map/locations/")

        returned_ids = {
            (item["id"], item["type"]) for item in response.data
        }
        self.assertNotIn((event.id, "event"), returned_ids)

    def test_empty_description_is_returned_as_empty_string(self):
        Destination.objects.create(
            name="No Description",
            interest=self.interest,
            latitude=Decimal("-26.204100"),
            longitude=Decimal("28.047300"),
            description=None,
        )

        response = self.client.get("/api/map/locations/")

        location = next(
            item for item in response.data
            if item["name"] == "No Description"
        )
        self.assertEqual(location["description"], "")
