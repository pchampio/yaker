from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Friendship(models.Model):
    """
        friends table
    """
    user = models.ForeignKey(User, related_name="user")
    friend = models.ForeignKey(User, related_name="friend")

    class Meta:
        unique_together = (("user", "friend"),)

