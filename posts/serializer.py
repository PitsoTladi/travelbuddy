from rest_framework import serializers
from .models import Post

class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate(self, data):
        event = data.get('event')
        destination = data.get('destination')

        if event and destination:
            raise serializers.ValidationError(
                "A post can be associated with either an event or a destination, not both."
            )
        return data