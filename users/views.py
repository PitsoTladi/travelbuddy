from rest_framework import viewsets
from .models import User
from .serializers import usersSerializers
from rest_framework.decorators import api_view
from rest_framework.response import Response



# Create your views here.
@api_view(['GET'])
def home(request):
    return Response({
        'message':"less get started"
    })


class userViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = usersSerializers