from rest_framework import serializers
from .models import User


class UsersSerializer(serializers.ModelSerializer):
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
            'interests',
            'role'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'email',
            'password',
           'role',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            email=validated_data['email'],
            password=password,
        )

        return user