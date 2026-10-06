from django.db import models

# Create your models here.
class Post(models.Model):
    created_by = models.ForeignKey('users.user' ,on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    image = models.ImageField(upload_to='posts/',blank=True, null = True)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey('events.Event',on_delete=models.CASCADE,blank=True,null=True,related_name='posts')
    destination = models.ForeignKey('destinations.Destination',on_delete=models.CASCADE,blank=True,null=True, related_name='posts')
    def __str__(self):
        return self.title