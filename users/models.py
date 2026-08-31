from django.db import models

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, )
    prev_destinations = models.TextField(blank=True, null=True)
    #ranks 1.rookie(suitcase)|2. voyager(compass)|3. explorer(map)|4.nomad(globe)
    '''
    | Action                       | Points |
| ---------------------------- | -----: |
| Write a review               |    +10 |
| Review gets a helpful/like   |     +5 |
| Add a photo                  |     +3 |
| Review a new destination     |    +10 |
| Review gets reported/removed |    −20 |
| Receive a “helpful” vote     |     +5 |
 1.rookie = 0-50 pts, 2.voyager = 51-100 pts, 3.explorer = 101-200 pts, 4.nomad = 201+ pts
    
    '''



    review_rank = models.CharField(max_length=10)
    bio = models.TextField(max_length=120, blank=True, null=True)
    avartar = models.ImageField(upload_to='avatars/', blank=True, null=True)


    def __str__(self):
        return self.name
