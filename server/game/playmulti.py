from django.contrib.auth.models import User

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder, json

from users.models import Followership
from .models import Game, Save

from .playsolo import *
from .score import *

import logging
logger = logging.getLogger(__name__)

class GameMultiLobby():

    # On cunsumer connect
    def newConsumerLobby(user, room):
        key = "lobby:"+room
        game = None
        if key in cache:
            game = cache.get(key)
            new_user = {"name":user.username,"id":user.id}
            if new_user in game["players"]:
                return {"group":(game)}

            if user.id in game["ban"]:
                return {
                    "user": ({"error": "You are not allowed to enter the lobby"}),
                    "user_close":True
            }

            loggedInLobby =  any(d.get("id", None) == user.id for d in game["players"])

            if "ingame" in game and not loggedInLobby:
                return {
                    "user": ({"error": "Game already started ;("}),
                    "user_close":True
            }

            if not loggedInLobby:
                game["players"].append(new_user)
                cache.set(key,game,60*10)
            logger.debug("User " + user.username + " has join a lobby : "+room)

        else:
            game = {"op": user.id, "players":[{"name":user.username,"id":user.id}],"ban":[]}
            cache.set(key,game , 60 * 2)
            logger.debug("User " + user.username + " has start a new lobby : "+room)

        return {"group":(game)}

    # on consumer message
    def user_input(content, channel_session):

        # INIT
        key = "lobby:"+channel_session["room"]
        if key not in cache:
            return {"group": ({"error" : "lobby discarded"}), "group_close":True}

        game = cache.get(key)

        user_id = int(channel_session["user"])

        # find user index in game cache
        user_index = None
        for i in reversed(range(len(game["players"]))):
            if game["players"][i]["id"] == user_id:
                user_index = i

        # END INIT

        # CMD leave
        if "leave" in content :
            if int(game["op"]) == user_id:
                cache.delete(key)
                return {"group" : ({"error" : "Operator canceled the lobby"}),"group_close":True}
            elif "ingame" not in game:
                if user_index is not None:
                    game["players"].pop(user_index)

                cache.set(key, game, 60 * 10)
                return {"group":(game),"user_close":True}

        # CMD ban
        if "ban" in content:
            ban = int(content["ban"])

            if int(game["op"]) == user_id and user_id != ban:
                for i in reversed(range(len(game["players"]))):
                    if game["players"][i].get("id") == ban:
                        game["players"].pop(i)

                if "ingame" in game and all_users_played(game):
                    # raz next num
                    for i in reversed(range(len(game["players"]))):
                        game["players"][i]["played"] = 0

                if ban not in game["ban"]:
                    game["ban"].append(ban)

                cache.set(key, game, 60 * 10)
                return {"group":(game)}
            else:
                return {"user": ({"error" : "Bad request"})}


        # CMD startGame
        if "startGame" in content and int(game["op"]) == user_id and "ingame" not in game:
            game["ingame"] = 1
            gameSession = Game.objects.order_by('?').first()

            for i in reversed(range(len(game["players"]))):
                game["players"][i]["played"] = 0
                GameMulti.create(game["players"][i]["id"], gameSession)

            cache.set(key, game, 60 * 10)
            GameManager, end = GameMulti.user_input(content,user_id)
            game["dice"] = GameManager["dice"]
            return {"group":(game)}

        # CMD d'un user pour jouer
        if "ingame" in game:
            if game["players"][user_index]["played"] == 1:
                return {"user": {"error": "Waiting for the other users to play !"}}


            GameManager, end = GameMulti.user_input(content,user_id)
            dice = 0
            if "dice" in GameManager:
                dice = GameManager["dice"]
                del GameManager["dice"]

            response = {"user": GameManager}

            if "error" not in GameManager:
                game["players"][user_index]["played"] = 1
                if end == True:
                    response["group"] = {i:GameManager[i] for i in GameManager if i!='board'}

                if all_users_played(game):
                    # end de la game unset ingame in game
                    if end == True:
                        del game["ingame"]
                    else:
                        # send next dice
                        response["group"] = {"dice": dice}

                    # raz next num
                    for i in reversed(range(len(game["players"]))):
                        game["players"][i]["played"] = 0

                cache.set(key, game, 60 * 10)
            return response
        return {"user": ({"error" : "Bad request"})}

def all_users_played(game):
    Nb_played = 0
    for i in reversed(range(len(game["players"]))):
        if game["players"][i]["played"] == 1:
            Nb_played += 1
    return Nb_played == len(game["players"])


class GameMulti(GameSolo):
    str_key_cache = ":multigame"
    @classmethod
    def create(cls, user, gameSession):
        key = 'user:'+ str(user) + cls.str_key_cache
        game = {}
        game['game_id'] = gameSession.id
        game['game_set'] = gameSession.game_set
        game['user_board'] = [[0]*5 for _ in range(5)]
        game['index_set'] = 0
        game['user_id'] = user
        cache.set(key, game, 120)

    def save(game, user_id):
        logger.info(str(user_id) + " end of Multi game")
        score = Score(game['user_board'])
        return({
            "user_id": user_id,
            "score": score,
            "board": game['user_board'],
            })

