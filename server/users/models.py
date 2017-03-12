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
    # when a user is unFollowing someone set it to false (prevent follower notif spam)
    isFollowing = models.BooleanField(default=True)

    def __str__(self):
        return "user: " + self.user.username + "___following : " + self.follower.username

    class Meta:
        unique_together = (("user", "follower"),)

    @classmethod
    def getFollowers(cls, user):
        """Get array of Users.username that *user* is following"""
        followers = (cls.objects.filter(user=user, isFollowing=True))
        followers_array = [ x.follower.username  for x in followers ]
        return followers_array

    @classmethod
    def deleteFollower(cls, user, follower):
        follower = cls.objects.get(user=user,
                        follower=User.objects.get(username=follower),
                        isFollowing=True
                                  )
        follower.isFollowing = False
        follower.save()


