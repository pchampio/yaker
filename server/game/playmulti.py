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
    """
    Lobby manager (user input for the game goes thought this)
    Warning it's boring AF

    Init
        User just joined a lobby
    Commands:
     user_input
        leave
        ban (id)
        startGame
        user_input using class GameMulti for the game itself (inherit sologame)
    """

    # On consumer connect
    def newConsumerLobby(user, room):
        key = "lobby:"+room
        game = None
        if key in cache: # si le lobby existe
            game = cache.get(key)
            new_user = {"name":user.username,"id":user.id}

            if user.id in game["ban"]: # user banned
                logger.info("User " + user.username + " has been banned from lobby :"+room)
                return {
                    "user": ({"error": "You are not allowed to enter the lobby"}),
                    "user_close":True
            }

            loggedInLobby =  any(d.get("id", None) == user.id for d in game["players"])

            if "ingame" in game and not loggedInLobby: # do not Accept user
                return {
                    "user": ({"error": "Game already started ;("}),
                    "user_close":True
            }

            if not loggedInLobby: # first connect of user in lobby
                game["players"].append(new_user)
                cache.set(key,game,60*10)
            logger.info("User " + user.username + " has join a lobby :"+room)

        else:  # Lobby init first user (op)
            game = {"op": user.id, "players":[{"name":user.username,"id":user.id}],"ban":[]}
            cache.set(key,game , 60 * 2)
            logger.info("User " + user.username + " has created a new lobby : "+room)


        # user no more disconnected
        user_index = None
        for i in reversed(range(len(game["players"]))):
            if game["players"][i]["id"] == user.id:
                user_index = i

        game["players"][user_index]["deco"] = False
        cache.set(key,game , 60 * 2)

        return {"group":game}

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

        if user_index == None:
            return {"user": ({"error" : "Bad request"})}

        # CMD leave
        if "leave" in content :
            if int(game["op"]) == user_id:
                cache.delete(key)
                logger.info("User " + game["players"][user_index]["name"] +
                            " has canceled lobby: "+channel_session["room"])
                return {"group" : ({"error" : "Operator canceled the lobby"}),"group_close":True}
            if user_index is not None:
                logger.info("User " + game["players"][user_index]["name"] +
                            " has leave lobby: "+channel_session["room"])
                if "ingame" not in game:
                    game["players"].pop(user_index)
                else:
                    game["players"][user_index]["deco"] = True # disconnected
                    cache.set(key, game, 60 * 10)
                    return {"group": game}

                cache.set(key, game, 60 * 10)
                return {"group":game,"user_close":True}

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
                return {"group":game}
            else:
                return {"user": ({"error" : "Bad request"})}


        # CMD startGame
        if "startGame" in content and int(game["op"]) == user_id and "ingame" not in game:
            game["ingame"] = 1
            count = Game.aggregate(count=Count('id'))['count']
            random_index = randint(0, count - 1)
            gameSession = Game.objects.all()[random_index]
            game["game_id"] = gameSession.id

            for i in reversed(range(len(game["players"]))):
                game["players"][i]["played"] = 0
                GameMulti.create(game["players"][i]["id"], gameSession)

            cache.set(key, game, 60 * 10)
            GameManager, end = GameMulti.user_input(content,user_id)
            game["dice"] = GameManager["dice"]

            logger.info("User " + game["players"][user_index]["name"] +
                        " has start a game in lobby: "+channel_session["room"])
            return {"group":game}

        # CMD d'un user pour jouer
        if "ingame" in game:

            if not game["game_id"] == GameMulti.getUserGameSet(user_id)["game_id"]:
                logger.warning("User id:" + str(user_id) + " might try to Cheat")

                # TODO Cleaner code!!
                game["players"].pop(user_index)
                game["ban"].append(user_id)

                if "ingame" in game and all_users_played(game):
                    # raz next num
                    for i in reversed(range(len(game["players"]))):
                        game["players"][i]["played"] = 0

                cache.set(key, game, 60 * 10)
                return {"group":game}


            if game["players"][user_index]["played"] == 1:
                GameManager, end = GameMulti.user_input({} ,user_id) # in case of reconnection
                GameManager["error"] = "Waiting for the other users to play !"
                del GameManager["dice"]
                return {"user": GameManager}


            GameManager, end = GameMulti.user_input(content,user_id)
            dice = 0
            if "dice" in GameManager:
                dice = GameManager["dice"]
                del GameManager["dice"]

            response = {"user": GameManager}

            if "error" not in GameManager:
                response["group"] = game

                game["players"][user_index]["played"] = 1
                if end == True:
                    # send user score to every users
                    logger.info("User " + game["players"][user_index]["name"] +
                                " end Multi game lobby: "+channel_session["room"]+
                                ", Score: " + str(GameManager['score']))
                    response["group"] = {i:GameManager[i] for i in GameManager if i!='board'}

                if all_users_played(game):
                    # send next dice
                    response["group"]["dice"] = dice

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

    @classmethod
    def getUserGameSet(cls,user_id):
        key = 'user:'+ str(user_id) + cls.str_key_cache
        return cache.get(key)


    def save(game, user_id):
        score = Score(game['user_board'])
        return{
            "user_id": user_id,
            "score": score,
            "board": game['user_board'],
            }

