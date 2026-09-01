from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    bio = models.TextField(
        max_length=120,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    review_points = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.name