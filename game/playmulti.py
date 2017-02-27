from django.contrib.auth.models import User

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder, json

from users.models import Followership
from .models import Game, Save

from .score import *

import logging
logger = logging.getLogger(__name__)

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
