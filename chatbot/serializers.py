
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=500,
        allow_blank=True,
        trim_whitespace=True,
    )
