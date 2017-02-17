from django.contrib.auth.models import User

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder, json

from users.models import Followership
from .models import Game, Save

from .score import *

import logging
logger = logging.getLogger(__name__)

class GameSolo():
    """ gère le jeux """

    def create(user):
        key = 'user:'+str(user.id)+':sologame'
        if key in cache:
            logger.debug("User " + user.username + " has restart cache saved game")
        else:
            gameSession = Game.get_or_create(user)
            logger.debug("User " + user.username + " has start a new game id : "
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
        # delete from cache

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

        followers = Followership.objects.filter(user=user)
        followers_array = [ x.follower  for x in followers ]

        for first in Save.objects.filter(
                game=game_save,
                user__in=followers_array
                ).order_by('-score'):
            firsts_followers.append(
                    {
                        "name" :first.user.username,
                        "score" :first.score,
                        "board" : jsonDec.decode(first.game_board),
                        }
                    )

            logger.debug("User " + user.username + " has complete lvl " +
                    str(game['game_id']) + " score : " + str(score))
            return({
                "score": score,
                "world_first":firsts,
                "followers_best":firsts_followers
                })


            def user_input(content, user_id):
                """
        check if user is malicious (or just curious) and give next value of board
        return dict and if ws should close or not
        """

        jsonDec = json.decoder.JSONDecoder()

        key = 'user:'+user_id+':sologame'
        game = cache.get(key)
        board = jsonDec.decode(game['game_set'])

        #  logger.debug(game)

        if "i" in content and 'j' in content:
            i = content['i']
            j = content['j']
            if isinstance(i, int) and isinstance(j,int):
                if 0 <= i < 5 and 0 <= j < 5 :
                    if game['user_board'][i][j] == 0:
                        game['user_board'][i][j] = board[game['index_set']]
                        game['index_set'] += 1
                        cache.set(key, game, 604800 * 2) # 2 week

                        # save the game
                        if game['index_set'] > 24:
                            end = GameSolo.save(game,user_id)
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

class GameMultiLobby():

    def newLobby(user, room):
        key = "lobby:"+room
        game = None
        if key in cache:
            game = cache.get(key)
            new_user = {"name":user.username,"id":user.id}
            if new_user in game['players']:
                return {"group":str(game)}

            if user.id in game['ban']:
                return {
                    "user":"You are bot allowed to enter this lobby",
                    "user_close":True
            }

            game['players'].append(new_user)
            cache.set(key,game,60*10)
            logger.debug("User " + user.username + " has join a lobby : "+room)

        else:
            game = {"op": user.id, "players":[{"name":user.username,"id":user.id}],"ban":[]}
            cache.set(key,game , 60 * 2)
            logger.debug("User " + user.username + " has start a new lobby : "+room)

        return {"group":str(game)}

    def user_input(content, channel_session):

        key = "lobby:"+channel_session['room']
        if key not in cache:
            return {"goup":"lobby discarded", "group_close":True}

        game = cache.get(key)

        user_id = int(channel_session['user'])

        loggedInLobby =  any(d.get('id', None) == user_id for d in game['players'])

        if "leave" in content or not loggedInLobby:
            if int(game['op']) == user_id:
                cache.delete(key)
                return {"group" :"Operator Canceled the game","group_close":True}
            else:
                for i in reversed(range(len(game['players']))):
                    if game['players'][i].get('id') == user_id:
                        game['players'].pop(i)

                cache.set(key, game, 60 * 10)
                return {"group":str(game),"user_close":True}

        if "ban" in content:
            ban = int(content['ban'])

            if int(game['op']) == user_id and user_id != ban:
                for i in reversed(range(len(game['players']))):
                    if game['players'][i].get('id') == ban:
                        game['players'].pop(i)

                if ban not in game['ban']:
                    game['ban'].append(ban)
                cache.set(key, game, 60 * 10)
                return {"group":str(game)}
            else:
                return {"user":"Bad request"}


        return {"user":"Bad request"}
