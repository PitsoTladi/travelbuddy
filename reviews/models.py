from django.db import models
from django.core.validators import *

# Create your models here.
class review(models.Model):
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    destination = models.ForeignKey(
        'destinations.Destination',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reviews'
    )

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        blank = True,
        null=True,
        related_name= 'reviews'
    )

    rating = models.PositiveIntegerField(
        validators= [MaxValueValidator(5), MinValueValidator(1)]
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.created_by}: {self.rating}'
