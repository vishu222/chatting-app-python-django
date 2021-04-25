from django.contrib.auth.models import User
from django.db import models

# Note: User is part of inbuilt django user model, which is being used in this application.

class Group(models.Model):
    group_name = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.group_name

class UserGroupMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return "{}-{}".format(self.user, self.group)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.sender, self.message)

    def __str__(self):
        return self.message


