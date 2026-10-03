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



    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)



