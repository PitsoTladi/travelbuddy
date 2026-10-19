from django.shortcuts import render

# Create your views here.

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .faq import find_faq_answer
from .serializers import ChatMessageSerializer


class ChatbotView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = find_faq_answer(serializer.validated_data["message"])

        return Response(
            result,
            status=status.HTTP_200_OK,
        )
