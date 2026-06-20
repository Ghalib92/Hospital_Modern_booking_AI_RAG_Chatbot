import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .rag import ChatbotUnavailable, answer_question
from .serializers import ChatRequestSerializer, ChatResponseSerializer

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """
    Ask the hospital medical assistant a question.

    RAG over a medical knowledge base, history-aware (pass prior turns in
    `history`), with an emergency-safety nudge. Returns 503 if not configured.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ChatRequestSerializer, responses={200: ChatResponseSerializer})
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = answer_question(
                serializer.validated_data["message"],
                serializer.validated_data.get("history"),
            )
        except ChatbotUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:  # pragma: no cover
            logger.exception("Chatbot failed to answer")
            return Response(
                {"detail": "The assistant failed to answer. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(result)
