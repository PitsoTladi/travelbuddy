from django.shortcuts import render
from .models import Event, Attendance
from rest_framework import viewsets
from .serializers import EventSerializer, attendanceSerializer


# Create your views here.
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializer