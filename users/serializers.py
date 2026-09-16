from rest_framework import serializers
from .models import User

class usersSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
                  'username',
                  'name',
                  'email',
                  'bio',
                  'avatar',
                  'budget',
                  'review_points',
                  'interests'
                  ]
