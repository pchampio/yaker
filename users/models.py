from __future__ import unicode_literals

from django.conf import settings

from django.contrib.auth.models import User
from django.db import models

class Followership(models.Model):
    """
        followers table
    """
    user = models.ForeignKey(User, related_name="Followership_user")
    follower = models.ForeignKey(User, related_name="Followership_follower")

    def __str__(self):
        return "user: " + self.user.username + "___following : " + self.follower.username

    class Meta:
        unique_together = (("user", "follower"),)

    def getFollowers(user):
        """Get array of Users.username that *user* is following"""
        followers = (Followership.objects.filter(user=user))
        followers_array = [ x.follower.username  for x in followers ]
        #  followers_array = filter(lambda a: a != user.username,followers_array)
        return followers_array

    def deleteFollower(user,follower):
        follower = (Followership.objects.
                    get(user=user,
                        follower=User.objects.get(
                        username=follower)))
        follower.delete()


