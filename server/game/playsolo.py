from django.contrib.auth.models import User

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder, json

from users.models import Followership
from .models import Game, Save

from .score import *

import logging
logger = logging.getLogger(__name__)

class GameSolo():
    """
    Game solo manager
    input user, saves, game creation
    Warning it's boring AF
    """

    str_key_cache = ":sologame"

    @classmethod
    def create(cls, user):
        key = 'user:'+str(user.id) + cls.str_key_cache
        if key in cache:
            logger.info("User " + user.username + " has restart cache saved game")
        else:
            gameSession = Game.get_or_create(user)
            logger.info("User " + user.username + " has start a new game id : "
                    + str(gameSession.id) )
            sologame = {}
            sologame['game_id'] = gameSession.id
            sologame['game_set'] = gameSession.game_set
            sologame['user_board'] = [[0]*5 for _ in range(5)]
            sologame['index_set'] = 0
            sologame['user_id'] = user.id
            cache.set(key, sologame, 120)

    def save(game, user_id):
        """ game saved in Save model after it ended"""
        jsonDec = json.decoder.JSONDecoder()

        user = User.objects.get(id=user_id)
        game_save = Game.objects.get(id=game['game_id'])
        game_board = json.dumps(game['user_board'])

        score = Score(game['user_board'])
        # save in Database
        Save.objects.create(user=user, game=game_save, score=score, game_board=game_board)

        # scores display

        firsts = []
        for first in Save.objects.filter(game=game_save).order_by('-score')[:10] :
            firsts.append(
                    {
                        "name" :first.user.username,
                        "score" :first.score,
                        }
                    )

        firsts_followers = []

        for first in Save.objects.filter(
                game=game_save,
                user__in=Followership.objects.filter(user=user, isFollowing=True).values_list('follower', flat=True)
                ).order_by('-score'):
            firsts_followers.append(
                    {
                        "name" :first.user.username,
                        "score" :first.score,
                        "board" : jsonDec.decode(first.game_board),
                        }
                    )

        logger.info("User " + user.username + " has complete lvl " +
                str(game['game_id']) + " score : " + str(score))
        return({
            "score": score,
            "board": game['user_board'],
            "world_first":firsts,
            "followers_best":firsts_followers
            })



    @classmethod
    def user_input(cls,content, user_id):
        """
        check if user is malicious (or just curious) and give next value of board
        return dict and if ws should close or not
        """

        jsonDec = json.decoder.JSONDecoder()

        key = 'user:'+str(user_id) + cls.str_key_cache
        game = cache.get(key)
        board = jsonDec.decode(game['game_set'])

        #  logger.info(game)
        if "skip" in content:
            cache.delete(key)
            return None,True # close ws

        if "i" in content and 'j' in content:
            i = content['i']
            j = content['j']
            if isinstance(i, int) and isinstance(j,int):
                if 0 <= i < 5 and 0 <= j < 5 :
                    if game['user_board'][i][j] == 0:
                        game['user_board'][i][j] = board[game['index_set']]
                        game['index_set'] += 1
                        cache.set(key, game, 604800 * 1) # 1 week

                        # save the game
                        if game['index_set'] > 24:
                            end = cls.save(game,user_id)
                            cache.delete(key)
                            return end,True # close ws

                        # keep going
                        return({
                            "dice": board[game['index_set']],
                            "board":game['user_board']
                            },False)

        return({
            "dice":board[game['index_set']],
            "error":"did you try to fool me",
            "board":game['user_board']
            },False)
