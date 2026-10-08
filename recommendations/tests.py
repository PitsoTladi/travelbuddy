from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from interests.models import Interest
from destinations.models import Destination
from events.models import Event


class RecommendationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='Password123!',
            role='adventure_seeker',
            budget=500
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='Password123!',
            role='adventure_seeker',
            budget=100
        )

        self.adventure = Interest.objects.create(name='Adventure')
        self.music = Interest.objects.create(name='Music')
        self.food = Interest.objects.create(name='Food')

        self.user.interests.add(self.adventure, self.music)

        # Destination that should score highly:
        # matching interest + within budget + good rating
        self.good_destination = Destination.objects.create(
            name='Gold Reef Adventure',
            created_by=self.other_user,
            price=300,
            rating=5.0,
            interest=self.adventure,
            city='Johannesburg'
        )

        # Doesn't match interest and is over budget
        self.expensive_destination = Destination.objects.create(
            name='Luxury Food Experience',
            created_by=self.other_user,
            price=1000,
            rating=4.0,
            interest=self.food,
            city='Johannesburg'
        )

        # Same interest but different city
        self.cape_destination = Destination.objects.create(
            name='Cape Adventure',
            created_by=self.other_user,
            price=200,
            rating=4.0,
            interest=self.adventure,
            city='Cape Town'
        )

        # Upcoming matching event
        self.good_event = Event.objects.create(
            name='Joburg Music Night',
            created_by=self.other_user,
            price=300,
            city='Johannesburg',
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=7),
            capacity=100
        )
        self.good_event.interest.add(self.music)

        # Past event — should NOT appear
        self.past_event = Event.objects.create(
            name='Old Music Festival',
            created_by=self.other_user,
            price=100,
            city='Johannesburg',
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=7),
            capacity=100
        )
        self.past_event.interest.add(self.music)

        self.client.force_authenticate(user=self.user)

    def test_recommendations_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse('recommendations')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_recommendations_return_data(self):
        response = self.client.get(
            reverse('recommendations')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreater(len(response.data), 0)

    def test_matching_interest_increases_destination_score(self):
        response = self.client.get(
            reverse('recommendations')
        )

        recommendation = next(
            item for item in response.data
            if item['data']['id'] == self.good_destination.id
        )

        # Interest match = 50
        # Within budget = 20
        # Rating 5 = 10
        # Total = 80
        self.assertEqual(recommendation['score'], 80)

    def test_budget_affects_destination_score(self):
        response = self.client.get(
            reverse('recommendations')
        )

        recommendation = next(
            item for item in response.data
            if item['data']['id'] == self.expensive_destination.id
        )

        # No interest match = 0
        # Over budget = 0
        # Rating 4 = 8
        self.assertEqual(recommendation['score'], 8)

    def test_recommendations_are_sorted_by_score(self):
        response = self.client.get(
            reverse('recommendations')
        )

        scores = [item['score'] for item in response.data]

        self.assertEqual(
            scores,
            sorted(scores, reverse=True)
        )

    def test_past_events_are_excluded(self):
        response = self.client.get(
            reverse('recommendations')
        )

        recommended_ids = [
            item['data']['id']
            for item in response.data
            if item['type'] == 'event'
        ]

        self.assertNotIn(
            self.past_event.id,
            recommended_ids
        )

    def test_upcoming_event_is_included(self):
        response = self.client.get(
            reverse('recommendations')
        )

        recommended_ids = [
            item['data']['id']
            for item in response.data
            if item['type'] == 'event'
        ]

        self.assertIn(
            self.good_event.id,
            recommended_ids
        )

    def test_city_filter(self):
        response = self.client.get(
            reverse('recommendations'),
            {'city': 'Johannesburg'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for item in response.data:
            self.assertEqual(
                item['data']['city'],
                'Johannesburg'
            )

    def test_destination_and_event_types_are_returned(self):
        response = self.client.get(
            reverse('recommendations')
        )

        types = {
            item['type']
            for item in response.data
        }

        self.assertIn('destination', types)
        self.assertIn('event', types)