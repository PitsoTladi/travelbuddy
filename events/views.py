from django.shortcuts import render
from .models import Event, Attendance
from rest_framework import viewsets
from .serializers import EventSerializer, AttendanceSerializer
from .permissions import isEventCreaterOwnerOrReadOnly
from rest_framework import permissions

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [isEventCreaterOwnerOrReadOnly]

  

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AttendanceViewSet(viewsets.ModelViewSet):
    #queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [isEventCreaterOwnerOrReadOnly]

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
       serializer.save(user=self.request.user)