from rest_framework import serializers
from .models import user

class usersSerializers(serializers.ModelSerializers):
    class Meta:
        model = user
        fields = [
                  'name',
                  'email',
                  'bio',
                  'avatar',
                  'budget',
                  'review_points',
                  'interests'
                  ]
