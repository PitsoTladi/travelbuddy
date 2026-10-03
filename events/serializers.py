from rest_framework import serializers
from .models import Event, Attendance

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_by']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        read_only_fields = ['user', 'date_of_attendance']
        fields = '__all__'
