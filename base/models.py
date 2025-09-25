from django.db import models
from django.contrib.auth.models import User
# For user built in diff import
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    # If topic specified below Topic => 'Topic'
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) 
    # null=True (Database-Level option) means can have NULL description 
    # blank=True (Validation-Level option) means field allowed to be empty when submitting form
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # Should specify a more complex ID for other projects
    # auto_now_add is for create timeStamp

    class Meta:
        ordering = ['-updated', '-created']
        # - makes it descending so newest shown first, 
        # this affects how the values are returned
    def __str__(self):
        return self.name
      
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # one to many or many to one RS here, on_delete=models.CASCADE means 
    # if parent gets deleted all children get deleted as well while SET_NULL doesnt
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
    
def profile_upload_path(instance, filename):
    return f"profiles/user_{instance.user_id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_img = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    # add more fields if you like, e.g. bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"