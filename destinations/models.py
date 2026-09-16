from django.db import models
from interests.models import Interest
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Destination(models.Model):
   
    name = models.CharField(max_length=100)

    description = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='destinations/',
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators= [MinValueValidator(0)]
    )

    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    city = models.CharField(default='Johannesburg', max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits =3, decimal_places = 2,validators=[MinValueValidator(0), MaxValueValidator(5)], default=0.00)
    def __str__(self):
        return self.name