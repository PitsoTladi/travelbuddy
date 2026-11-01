
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from django.test import override_settings

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


class GoogleLoginTests(APITestCase):
    url = "/api/auth/google/"

    def setUp(self):
        self.client_id_override = override_settings(
            GOOGLE_OAUTH_CLIENT_ID="test-google-client-id"
        )
        self.client_id_override.enable()
        self.addCleanup(self.client_id_override.disable)

    def test_missing_credential_is_rejected(self):
        response = self.client.post(
            self.url, {}, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("users.views.id_token.verify_oauth2_token")
    def test_invalid_google_token_is_rejected(self, mock_verify):
        mock_verify.side_effect = ValueError("Invalid token")

        response = self.client.post(
            self.url,
            {"credential": "invalid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertFalse(User.objects.exists())

    @patch("users.views.id_token.verify_oauth2_token")
    def test_verified_google_user_receives_jwt_tokens(
        self, mock_verify
    ):
        mock_verify.return_value = {
            "sub": "google-sub-123",
            "email": "googleuser@example.com",
            "email_verified": True,
            "name": "Google Test User",
        }

        response = self.client.post(
            self.url,
            {"credential": "mock-valid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        user = User.objects.get(
            email="googleuser@example.com"
        )
        self.assertEqual(user.google_sub, "google-sub-123")
        self.assertEqual(user.name, "Google Test User")
        self.assertEqual(user.role, "adventure_seeker")
        self.assertFalse(user.has_usable_password())

        mock_verify.assert_called_once()
        self.assertEqual(
            mock_verify.call_args.kwargs["audience"],
            "test-google-client-id",
        )

    @patch("users.views.id_token.verify_oauth2_token")
    def test_existing_email_is_not_automatically_linked(
        self, mock_verify
    ):
        existing_user = User.objects.create_user(
            username="existinggoogle",
            name="Existing User",
            email="existinggoogle@example.com",
            password="SecurePass123!",
        )

        mock_verify.return_value = {
            "sub": "different-google-sub",
            "email": "existinggoogle@example.com",
            "email_verified": True,
            "name": "Existing Google User",
        }

        response = self.client.post(
            self.url,
            {"credential": "mock-valid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        existing_user.refresh_from_db()
        self.assertIsNone(existing_user.google_sub)
        self.assertEqual(User.objects.count(), 1)
