from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Followership(models.Model):
    """
        followers table
    """
    user = models.ForeignKey(User, related_name="user")
    follower = models.ForeignKey(User, related_name="follower")

    class Meta:
        unique_together = (("user", "follower"),)

