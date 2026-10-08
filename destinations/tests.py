from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from interests.models import Interest
from destinations.models import Destination


class DestinationPermissionTests(APITestCase):

    def setUp(self):
        self.interest = Interest.objects.create(
            name='Adventure'
        )

        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='Password123!',
            name='Adventure Seeker',
            role='adventure_seeker',
            budget=500
        )

        self.business = User.objects.create_user(
            username='business',
            email='business@test.com',
            password='Password123!',
            name='Business Creator',
            role='business_creator',
            budget=1000
        )

        self.other_business = User.objects.create_user(
            username='business2',
            email='business2@test.com',
            password='Password123!',
            name='Other Business',
            role='business_creator',
            budget=1000
        )

        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Testing ownership',
            price=200,
            interest=self.interest,
            city='Johannesburg',
            rating=4,
            created_by=self.business
        )

        self.url = reverse('destination-list')

    # ----------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------

    def test_adventure_seeker_cannot_create_destination(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.url,
            {
                'name': 'Unauthorized Destination',
                'description': 'Should fail',
                'price': 100,
                'interest': self.interest.id,
                'city': 'Johannesburg',
                'rating': 4
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_business_creator_can_create_destination(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.post(
            self.url,
            {
                'name': 'New Destination',
                'description': 'Created by business',
                'price': 300,
                'interest': self.interest.id,
                'city': 'Johannesburg',
                'rating': 5
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['created_by'],
            self.business.id
        )

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------

    def test_business_creator_can_update_own_destination(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(
            reverse(
                'destination-detail',
                kwargs={'pk': self.destination.id}
            ),
            {
                'name': 'Updated Destination'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_business_creator_cannot_update_another_business_destination(self):
        self.client.force_authenticate(user=self.other_business)

        response = self.client.patch(
            reverse(
                'destination-detail',
                kwargs={'pk': self.destination.id}
            ),
            {
                'name': 'Hacked Destination'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_adventure_seeker_cannot_update_destination(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.patch(
            reverse(
                'destination-detail',
                kwargs={'pk': self.destination.id}
            ),
            {
                'name': 'Hacked Destination'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------

    def test_business_creator_can_delete_own_destination(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.delete(
            reverse(
                'destination-detail',
                kwargs={'pk': self.destination.id}
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_business_creator_cannot_delete_another_business_destination(self):
        self.client.force_authenticate(user=self.other_business)

        response = self.client.delete(
            reverse(
                'destination-detail',
                kwargs={'pk': self.destination.id}
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

class DestinationValidationTests(APITestCase):

    def setUp(self):
        self.interest = Interest.objects.create(
            name='Adventure'
        )

        self.business = User.objects.create_user(
            username='business',
            email='business@test.com',
            password='Password123!',
            name='Business Creator',
            role='business_creator',
            budget=1000
        )

        self.url = reverse('destination-list')

        self.client.force_authenticate(
            user=self.business
        )

    def test_destination_rejects_negative_price(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Negative Price',
                'description': 'Should fail',
                'price': -100,
                'interest': self.interest.id,
                'city': 'Johannesburg',
                'rating': 4
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_destination_rejects_rating_above_five(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Invalid Rating',
                'description': 'Should fail',
                'price': 100,
                'interest': self.interest.id,
                'city': 'Johannesburg',
                'rating': 6
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_destination_rejects_negative_rating(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Invalid Rating',
                'description': 'Should fail',
                'price': 100,
                'interest': self.interest.id,
                'city': 'Johannesburg',
                'rating': -1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

class DestinationFilteringTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='business',
            email='business@test.com',
            password='Password123!',
            role='business_creator'
        )

        adventure = Interest.objects.create(name='Adventure')
        nature = Interest.objects.create(name='Nature')

        Destination.objects.create(
            name='Gold Reef City',
            created_by=self.user,
            price=450,
            rating=4.5,
            interest=adventure,
            city='Johannesburg'
        )

        Destination.objects.create(
            name='Zoo Lake',
            created_by=self.user,
            price=100,
            rating=4.0,
            interest=nature,
            city='Johannesburg'
        )

        Destination.objects.create(
            name='Cape Point',
            created_by=self.user,
            price=600,
            rating=4.9,
            interest=adventure,
            city='Cape Town'
        )

        self.client.force_authenticate(user=self.user)

    def test_filter_by_city(self):
        response = self.client.get(
            reverse('destination-list'),
            {'city': 'Johannesburg'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for destination in response.data:
            self.assertEqual(destination['city'], 'Johannesburg')

    def test_filter_by_max_price(self):
        response = self.client.get(
            reverse('destination-list'),
            {'price__lte': 300}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Zoo Lake')

    def test_filter_by_min_rating(self):
        response = self.client.get(
            reverse('destination-list'),
            {'rating__gte': 4.5}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for destination in response.data:
            self.assertGreaterEqual(float(destination['rating']), 4.5)

    def test_search_by_name(self):
        response = self.client.get(
            reverse('destination-list'),
            {'search': 'Gold'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Gold Reef City')

    def test_combine_filters(self):
        response = self.client.get(
            reverse('destination-list'),
            {
                'city': 'Johannesburg',
                'price__lte': 300
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Zoo Lake')

    def test_filter_by_interest(self):
        adventure = Interest.objects.get(name='Adventure')

        response = self.client.get(
            reverse('destination-list'),
            {'interest': adventure.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for destination in response.data:
            self.assertEqual(destination['interest'], adventure.id)