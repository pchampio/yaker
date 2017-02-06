from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

import random as r
import json

def create_game_set():
    set = []
    for i in range(1,25) :
        set.append(r.randint(1,6) + r.randint(1,6))

    if Game.objects.filter(game_set=set).exists():
        set = create_game_set()
    return json.dumps(set)

class Game(models.Model):
    """Game table"""
    game_set = models.CharField(max_length=25, default=create_game_set)

class Save(models.Model):
    """ Save table"""
    user = models.ForeignKey(User, related_name="Save_user")
    id_game = models.ForeignKey(Game, related_name="Save_game_id")
    date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=False)
    game_board = models.CharField(max_length=25, default='')

    class Meta:
            unique_together = (('user', 'id_game'),)
