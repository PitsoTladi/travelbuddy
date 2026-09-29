from rest_framework import viewsets
from .models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UsersSerializer



# Create your views here.


class userViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user =serializer.save()

        return Response({
            'message': 'user successfuly registered'
        },
        status= status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status = status.HTTP_400_BAD_REQUEST
    )