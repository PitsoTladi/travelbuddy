from rest_framework import serializers
from .models import review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = review
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at','updated_at']

    def validate(self,data):
        event = data.get('event')
        destination = data.get('destination')

        if event and destination:
            raise serializers.ValidationError(
                "Review can either be associated with event or destination not both"
            )
        elif not event and not destination:
            raise serializers.ValidationError(
                "Review an event or destination bruv"
            )

        return data