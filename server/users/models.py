from __future__ import unicode_literals

from django.conf import settings

from django.contrib.auth.models import User
from django.db import models

class Followership(models.Model):
    """
        followers table
    """
    users = models.ManyToManyField(User)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return "__Status: " + str(self.accepted)

    @classmethod
    def getFollowers(cls, user):
        """Get array of Users.username that *user* is following"""
        followers = (cls.objects.filter(user=user))
        followers_array = [ x.follower.username  for x in followers ]
        #  followers_array = filter(lambda a: a != user.username,followers_array)
        return followers_array

    @classmethod
    def deleteFollower(cls, user, follower):
        follower = (cls.objects.
                    get(user=user,
                        follower=User.objects.get(
                        username=follower)))
        follower.delete()


