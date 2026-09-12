from rest_framework import viewsets
from .models import User
from .serializers import usersSerializers
from rest_framework.decorators import api_view
from rest_framework.response import Response



# Create your views here.


class userViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = usersSerializers