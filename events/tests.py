from datetime import date, timedelta

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from interests.models import Interest
from events.models import Event


class EventPermissionTests(APITestCase):

    def setUp(self):
        self.interest = Interest.objects.create(
            name='Music'
        )

        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='Password123!',
            name='Adventure Seeker',
            role='adventure_seeker',
            budget=500
        )

        self.event_creator = User.objects.create_user(
            username='eventcreator',
            email='eventcreator@test.com',
            password='Password123!',
            name='Event Creator',
            role='event_creator',
            budget=1000
        )

        self.other_event_creator = User.objects.create_user(
            username='eventcreator2',
            email='eventcreator2@test.com',
            password='Password123!',
            name='Other Event Creator',
            role='event_creator',
            budget=1000
        )

        self.event = Event.objects.create(
            name='Test Event',
            description='Testing ownership',
            price=200,
            city='Johannesburg',
            category='Music',
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=11),
            capacity=100,
            created_by=self.event_creator
        )

        self.event.interest.add(self.interest)

        self.url = reverse('event-list')

    # ----------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------

    def test_adventure_seeker_cannot_create_event(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.url,
            {
                'name': 'Unauthorized Event',
                'description': 'Should fail',
                'price': 100,
                'city': 'Johannesburg',
                'category': 'Music',
                'start_date': str(date.today() + timedelta(days=20)),
                'end_date': str(date.today() + timedelta(days=21)),
                'capacity': 100,
                'interest': [self.interest.id]
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_event_creator_can_create_event(self):
        self.client.force_authenticate(user=self.event_creator)

        response = self.client.post(
            self.url,
            {
                'name': 'New Event',
                'description': 'Created by event creator',
                'price': 300,
                'city': 'Johannesburg',
                'category': 'Music',
                'start_date': str(date.today() + timedelta(days=20)),
                'end_date': str(date.today() + timedelta(days=21)),
                'capacity': 100,
                'interest': [self.interest.id]
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['created_by'],
            self.event_creator.id
        )

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------

    def test_event_creator_can_update_own_event(self):
        self.client.force_authenticate(user=self.event_creator)

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={'pk': self.event.id}
            ),
            {
                'name': 'Updated Event'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_event_creator_cannot_update_another_creator_event(self):
        self.client.force_authenticate(
            user=self.other_event_creator
        )

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={'pk': self.event.id}
            ),
            {
                'name': 'Hacked Event'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_adventure_seeker_cannot_update_event(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={'pk': self.event.id}
            ),
            {
                'name': 'Hacked Event'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------

    def test_event_creator_can_delete_own_event(self):
        self.client.force_authenticate(user=self.event_creator)

        response = self.client.delete(
            reverse(
                'event-detail',
                kwargs={'pk': self.event.id}
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_event_creator_cannot_delete_another_creator_event(self):
        self.client.force_authenticate(
            user=self.other_event_creator
        )

        response = self.client.delete(
            reverse(
                'event-detail',
                kwargs={'pk': self.event.id}
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

class EventFilteringTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='eventcreator',
            email='eventcreator@test.com',
            password='Password123!',
            role='event_creator'
        )

        music = Interest.objects.create(name='Music')
        food = Interest.objects.create(name='Food')

        event1 = Event.objects.create(
            name='Joburg Jazz Night',
            created_by=self.user,
            price=300,
            city='Johannesburg',
            category='Music'
        )
        event1.interest.add(music)

        event2 = Event.objects.create(
            name='Food Festival',
            created_by=self.user,
            price=150,
            city='Johannesburg',
            category='Food'
        )
        event2.interest.add(food)

        event3 = Event.objects.create(
            name='Cape Music Fest',
            created_by=self.user,
            price=500,
            city='Cape Town',
            category='Music'
        )
        event3.interest.add(music)

        self.client.force_authenticate(user=self.user)

    def test_filter_by_city(self):
        response = self.client.get(
            reverse('event-list'),
            {'city': 'Johannesburg'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for event in response.data:
            self.assertEqual(event['city'], 'Johannesburg')

    def test_filter_by_max_price(self):
        response = self.client.get(
            reverse('event-list'),
            {'price__lte': 300}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for event in response.data:
            self.assertLessEqual(float(event['price']), 300)

    def test_filter_by_category(self):
        response = self.client.get(
            reverse('event-list'),
            {'category': 'Music'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for event in response.data:
            self.assertEqual(event['category'], 'Music')

    def test_search_by_name(self):
        response = self.client.get(
            reverse('event-list'),
            {'search': 'Jazz'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Joburg Jazz Night')

    def test_combine_filters(self):
        response = self.client.get(
            reverse('event-list'),
            {
                'city': 'Johannesburg',
                'price__lte': 200
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Food Festival')

    def test_filter_by_interest(self):
        music = Interest.objects.get(name='Music')

        response = self.client.get(
            reverse('event-list'),
            {'interest': music.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)