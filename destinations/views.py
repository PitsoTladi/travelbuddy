from django.shortcuts import render
from .models import Destination

from rest_framework import viewsets
from .serializers import DestinationSerializer, AttendanceSerializer

# Create your views here.
class DestinationViewSets(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

