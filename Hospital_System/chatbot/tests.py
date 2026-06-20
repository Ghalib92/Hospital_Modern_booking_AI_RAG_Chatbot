from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .rag import detect_emergency


class ChatbotTests(APITestCase):
    def test_detect_emergency(self):
        self.assertTrue(detect_emergency("I have severe chest pain"))
        self.assertFalse(detect_emergency("I have a mild cold"))

    def test_emergency_short_circuits(self):
        resp = self.client.post(reverse("chat"), {"message": "I can't breathe"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["emergency"])

    @override_settings(OPENAI_API_KEY="", PINECONE_API_KEY="")
    def test_unconfigured_returns_503(self):
        from chatbot import rag
        rag.reset_cache()
        resp = self.client.post(reverse("chat"), {"message": "What is malaria?"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_empty_message_rejected(self):
        self.assertEqual(
            self.client.post(reverse("chat"), {"message": ""}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("chatbot.views.answer_question")
    def test_answer_with_sources(self, mock_answer):
        mock_answer.return_value = {
            "answer": "Stay hydrated.", "sources": [{"source": "med.pdf", "page": 3}],
            "emergency": False, "disclaimer": "...",
        }
        resp = self.client.post(reverse("chat"), {"message": "fever advice?"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["sources"][0]["source"], "med.pdf")
