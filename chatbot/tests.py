
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from .faq import find_faq_answer


class FAQMatchingTests(APITestCase):
    def test_booking_question_returns_booking_answer(self):
        result = find_faq_answer("How do I book an event?")
        self.assertIn("cannot book the same event twice", result["answer"])

    def test_event_question_returns_event_answer(self):
        result = find_faq_answer("What events are available?")
        self.assertIn("browse events", result["answer"])

    def test_cancellation_question_returns_cancellation_answer(self):
        result = find_faq_answer("How do I cancel my booking?")
        self.assertIn("cancel your own event booking", result["answer"])

    def test_empty_message_requests_a_question(self):
        result = find_faq_answer("")
        self.assertIn("enter a question", result["answer"])

    def test_whitespace_message_requests_a_question(self):
        result = find_faq_answer("   ")
        self.assertIn("enter a question", result["answer"])

    def test_unknown_question_returns_fallback(self):
        result = find_faq_answer("What is the weather on Mars?")
        self.assertIn("not sure", result["answer"])

    def test_matching_is_case_insensitive(self):
        result = find_faq_answer("HOW DO I BOOK AN EVENT?")
        self.assertIn("cannot book the same event twice", result["answer"])

    def test_destination_question_returns_destination_answer(self):
        result = find_faq_answer("Where can I find destinations?")
        self.assertIn("explore destinations", result["answer"])


class ChatbotAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("chatbot")

    def test_chatbot_answers_valid_question(self):
        response = self.client.post(
            self.url,
            {"message": "How do I book an event?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cannot book the same event twice", response.data["answer"])
        self.assertIn("suggestions", response.data)

    def test_chatbot_accepts_empty_message(self):
        response = self.client.post(
            self.url,
            {"message": ""},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("enter a question", response.data["answer"])

    def test_chatbot_rejects_missing_message(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chatbot_rejects_message_over_500_characters(self):
        response = self.client.post(
            self.url,
            {"message": "a" * 501},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chatbot_does_not_require_authentication(self):
        response = self.client.post(
            self.url,
            {"message": "What events are available?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
