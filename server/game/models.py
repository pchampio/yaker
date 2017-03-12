from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

import random, json, os, logging

logger = logging.getLogger(__name__)


def create_game_set():
    """Generate a list of 25 Dicex2 roll"""
    #  https://xkcd.com/221/
    set = []
    seed_bytes=128
    for i in range(0,25) :
        random.seed(os.urandom(seed_bytes))
        set.append(random.randint(1,6) + random.randint(1,6))

    if Game.objects.filter(game_set=set).exists():
        set = create_game_set()
    return json.dumps(set)

class Game(models.Model):
    """Game table"""
    game_set = models.CharField(max_length=100, default=create_game_set)


    def __str__(self):
        return "game_id: " + str(self.id) + "___gameSet: " + str(self.game_set)

    def get_or_create(user):
        """
        Check if user has a unplayed set available in Game (using Save model)
        if not create new set
        """
        gameObj = Game.objects.exclude(
            Save_game__in = Save.objects.filter(
                user=user
            )
        )
        if gameObj.count() == 0:
            #  new set
            logger.debug("Create new game set (" + user.username + " has complete all exists one)")
            return Game.objects.create()
        else:
            # get existing one
            return gameObj[random.randint(0,gameObj.count()-1)]



class Save(models.Model):
    """ Save table"""
    user = models.ForeignKey(User, related_name="Save_user")
    game = models.ForeignKey(Game, related_name="Save_game")
    date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=False)
    game_board = models.CharField(max_length=100, default='')

    def __str__(self):
        return "user: " + self.user.username + "___game: " + str(self.game.id) + "___score: " + str(self.score)

    class Meta:
            unique_together = (('user', 'game'),)