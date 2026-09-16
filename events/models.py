from django.db import models



# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    interest = models.ManyToManyField('interests.Interest')
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
    category = models.CharField(max_length=100, blank=True, null=True)
    destination = models.ForeignKey('destinations.Destination', on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
            return self.name



class Attendance(models.Model):
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE
    
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date_of_attendance = models.DateTimeField(auto_now_add=True)
    

    
    
    def __str__(self):
        return f"{self.user} - {self.event}"