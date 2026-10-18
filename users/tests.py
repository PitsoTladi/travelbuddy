
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    url = "/api/register/"

    def test_register_adventure_seeker(self):
        response = self.client.post(self.url, {
            "username": "seeker1",
            "name": "Test Seeker",
            "email": "seeker@example.com",
            "password": "SecurePass123!",
            "role": "adventure_seeker",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="seeker1")
        self.assertEqual(user.role, "adventure_seeker")
        self.assertTrue(user.check_password("SecurePass123!"))

    def test_register_business_creator(self):
        response = self.client.post(self.url, {
            "username": "business1",
            "name": "Test Business",
            "email": "business@example.com",
            "password": "SecurePass123!",
            "role": "business_creator",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="business1")
        self.assertEqual(user.role, "business_creator")

    def test_register_event_creator(self):
        response = self.client.post(self.url, {
            "username": "event1",
            "name": "Test Event Creator",
            "email": "event@example.com",
            "password": "SecurePass123!",
            "role": "event_creator",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="event1")
        self.assertEqual(user.role, "event_creator")

    def test_invalid_role_is_rejected(self):
        response = self.client.post(self.url, {
            "username": "invalidrole",
            "name": "Invalid Role",
            "email": "invalid@example.com",
            "password": "SecurePass123!",
            "role": "admin",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="invalidrole").exists())

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="existing",
            name="Existing User",
            email="existing@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(self.url, {
            "username": "existing",
            "name": "Duplicate User",
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "role": "adventure_seeker",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="anotheruser",
            name="Another User",
            email="taken@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(self.url, {
            "username": "newuser",
            "name": "New User",
            "email": "taken@example.com",
            "password": "SecurePass123!",
            "role": "adventure_seeker",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileSecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            name="Profile User",
            email="profile@example.com",
            password="SecurePass123!",
            role="adventure_seeker",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            name="Other User",
            email="other@example.com",
            password="SecurePass123!",
        )
        self.client.force_authenticate(user=self.user)

    def test_user_cannot_retrieve_another_profile(self):
        response = self.client.get(
            f"/api/users/{self.other_user.pk}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_change_own_role_or_review_points(self):
        response = self.client.patch(
            f"/api/users/{self.user.pk}/",
            {
                "role": "business_creator",
                "review_points": 9999,
                "bio": "Updated bio",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "adventure_seeker")
        self.assertEqual(self.user.review_points, 0)
        self.assertEqual(self.user.bio, "Updated bio")

    def test_user_list_only_contains_own_profile(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "profileuser")