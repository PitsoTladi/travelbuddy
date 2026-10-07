from django.shortcuts import render
from .models import Destination
from .permissions import IsBusinessCreatorOwnerOrReadOnly

from rest_framework import viewsets
from .serializers import DestinationSerializer

# Create your views here.
class DestinationViewSets(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsBusinessCreatorOwnerOrReadOnly]

    filterset_fields = {
        'city': ['exact'],
        'price': ['exact','gte','lte'],
        'rating':['exact','gte','lte'],
         'interest': ['exact'],
    }

    search_fields = ['name','description']

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)



