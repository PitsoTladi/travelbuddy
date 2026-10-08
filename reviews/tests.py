from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from interests.models import Interest
from destinations.models import Destination
from events.models import Event
from reviews.models import review


class ReviewValidationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='Password123!',
            name='Reviewer',
            role='adventure_seeker',
            budget=500
        )

        self.interest = Interest.objects.create(
            name='Music'
        )

        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test destination',
            price=200,
            interest=self.interest,
            city='Johannesburg',
            rating=4,
            created_by=self.user
        )

        self.event = Event.objects.create(
            name='Test Event',
            description='Test event',
            price=200,
            city='Johannesburg',
            category='Music',
            created_by=self.user,
            capacity=100
        )

        self.event.interest.add(self.interest)

        self.url = reverse('review-list')

        self.client.force_authenticate(
            user=self.user
        )

    def test_review_rejects_rating_below_one(self):

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'rating': 0,
                'content': 'Bad rating'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_review_rejects_rating_above_five(self):

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'rating': 6,
                'content': 'Bad rating'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_review_requires_destination_or_event(self):

        response = self.client.post(
            self.url,
            {
                'rating': 5,
                'content': 'No target'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_review_cannot_have_destination_and_event(self):

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'event': self.event.id,
                'rating': 5,
                'content': 'Two targets'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )