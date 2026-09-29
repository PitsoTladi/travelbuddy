from rest_framework import serializers
from .models import Event, Attendance

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class attendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        read_only_fields = ['created_by']
        fields = '__all__'