from rest_framework import serializers
from .models import Destination

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        
        fields = '__all__'
        read_only_fields = ['created_by']