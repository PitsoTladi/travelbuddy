from django.shortcuts import render
from rest_framework import viewsets
from .serializer import postSerializer
from .permissions import IsOwnerOrReadOnly
from .models import  Post
# Create your views here.

class postViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = postSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by = self.request.user)