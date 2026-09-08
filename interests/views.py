from django.shortcuts import render
from .models import Interest
from rest_framework import viewsets
from .serializers import InterestSerializer
# Create your views here.

class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
