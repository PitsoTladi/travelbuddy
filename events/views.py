from django.shortcuts import render
from .models import Event, Attendance
from rest_framework import viewsets
from .serializers import EventSerializer, AttendanceSerializer
from .permissions import isEventCreaterOwnerOrReadOnly
from rest_framework import permissions

from django.db import transaction
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [isEventCreaterOwnerOrReadOnly]

    filterset_fields = {
        'city': ['exact'],
        'price': ['exact', 'gte', 'lte'],
        'category': ['exact'],
        'start_date': ['exact', 'gte', 'lte'],
        'end_date': ['exact', 'gte', 'lte'],
        'interest': ['exact'],
    }

    search_fields = ['name', 'description']

  

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data['event']

        with transaction.atomic():
            # Lock the event while checking booking capacity.
            event = Event.objects.select_for_update().get(pk=event.pk)

            if event.capacity == 0:
                raise ValidationError({
                    'event': 'This event is not open for bookings.'
                })

            existing = Attendance.objects.filter(
                event=event,
                user=request.user
            ).exists()

            if existing:
                raise ValidationError({
                    'event': 'You have already booked this event.'
                })

            bookings = Attendance.objects.filter(event=event).count()

            if bookings >= event.capacity:
                raise ValidationError({
                    'event': 'This event is fully booked.'
                })

            booking = Attendance.objects.create(
                event=event,
                user=request.user
            )

        output = self.get_serializer(booking)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED
        )