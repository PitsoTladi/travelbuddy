from django.shortcuts import render
from rest_framework import viewsets
from .models import review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly
# Create your views here.

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
         serializer.save(created_by = self.request.user)
