from django.db import models
#model for users
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host =  models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null = True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    #many to many relationship
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    update  = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        #you can order by desc, or asc
        ordering = ['-update', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    update  = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        #you can order by desc, or asc
        ordering = ['-update', '-created']

    def __str__(self):
        #it will show the first 50 characters
        return self.body[0:50]