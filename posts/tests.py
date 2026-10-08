from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from interests.models import Interest
from destinations.models import Destination
from events.models import Event


class PostValidationTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='poster',
            email='poster@test.com',
            password='Password123!',
            name='Poster',
            role='adventure_seeker',
            budget=500
        )

        self.interest = Interest.objects.create(
            name='Music'
        )

        self.destination = Destination.objects.create(
            name='Test Destination',
            price=200,
            interest=self.interest,
            city='Johannesburg',
            rating=4,
            created_by=self.user
        )

        self.event = Event.objects.create(
            name='Test Event',
            price=200,
            city='Johannesburg',
            category='Music',
            capacity=100,
            created_by=self.user
        )

        self.event.interest.add(self.interest)

        self.url = reverse('post-list')

        self.client.force_authenticate(
            user=self.user
        )

    def test_post_cannot_have_event_and_destination(self):

        response = self.client.post(
            self.url,
            {
                'title': 'Invalid Post',
                'content': 'This should fail',
                'event': self.event.id,
                'destination': self.destination.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )