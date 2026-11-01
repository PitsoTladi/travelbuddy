from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from interests.models import Interest
from destinations.models import Destination


User = get_user_model()


class DestinationPermissionTests(APITestCase):

    def setUp(self):
        # Users
        self.seeker = User.objects.create_user(
            username='test_seeker',
            email='seeker@test.com',
            password='Password123!',
            name='Test Seeker',
            role='adventure_seeker',
            budget=500
        )

        self.business = User.objects.create_user(
            username='test_business',
            email='business@test.com',
            password='Password123!',
            name='Test Business',
            role='business_creator',
            budget=1000
        )

        self.event_creator = User.objects.create_user(
            username='test_event_creator',
            email='event@test.com',
            password='Password123!',
            name='Test Event Creator',
            role='event_creator',
            budget=1000
        )

        # Interest
        self.interest = Interest.objects.create(
            name='Test Interest'
        )

        # Existing destination owned by Business Creator
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Testing ownership',
            price=300,
            interest=self.interest,
            city='Johannesburg',
            rating=4,
            created_by=self.business
        )

        self.url = '/api/destinations/'

        self.destination_data = {
            'name': 'New Destination',
            'description': 'Created during automated testing',
            'price': 200,
            'interest': self.interest.id,
            'city': 'Johannesburg',
            'rating': 4
        }

    # ==========================================================
    # CREATE PERMISSIONS
    # ==========================================================

    def test_adventure_seeker_cannot_create_destination(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.url,
            self.destination_data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_event_creator_cannot_create_destination(self):
        self.client.force_authenticate(user=self.event_creator)

        response = self.client.post(
            self.url,
            self.destination_data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_business_creator_can_create_destination(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.post(
            self.url,
            self.destination_data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['created_by'],
            self.business.id
        )

    # ==========================================================
    # OWNERSHIP
    # ==========================================================

    def test_owner_can_edit_destination(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(
            f'{self.url}{self.destination.id}/',
            {
                'name': 'Updated Destination'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_other_business_creator_cannot_edit_destination(self):

        other_business = User.objects.create_user(
            username='other_business',
            email='otherbusiness@test.com',
            password='Password123!',
            name='Other Business',
            role='business_creator'
        )

        self.client.force_authenticate(user=other_business)

        response = self.client.patch(
            f'{self.url}{self.destination.id}/',
            {
                'name': 'Hacked Destination'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_other_business_creator_cannot_delete_destination(self):

        other_business = User.objects.create_user(
            username='other_business2',
            email='otherbusiness2@test.com',
            password='Password123!',
            name='Other Business 2',
            role='business_creator'
        )

        self.client.force_authenticate(user=other_business)

        response = self.client.delete(
            f'{self.url}{self.destination.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )