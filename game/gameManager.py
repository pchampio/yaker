from django.contrib.auth.models import User

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder, json

from users.models import Followership
from .models import Game, Save

import logging
logger = logging.getLogger(__name__)

class GameManger():
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
                            end = GameManger.save(game,user_id)
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



def is_Sorted(lst):
    if len(lst) == 1:
       return True
    return lst[0] < lst[1] and is_Sorted(lst[1:])

def diagonal(matrix):
    return ([matrix[i][i] for i in range(min(len(matrix[0]),len(matrix)))])

def score_in_row(row):
    row_count = []
    pts = 0
    for item in row:
         row_count.append(row.count(item))

    if row_count.count(2) == 4: # 2 paire
        pts += 3
    elif row_count.count(4) == 4: # carre
        pts += 6
    elif row_count.count(5) == 5: # 5x
        pts += 8
    elif row_count.count(3) == 3 and row_count.count(2) == 2: # full
        pts += 6
    elif row_count.count(3) == 3: # brelan
        pts += 3
    elif row_count.count(2) == 2: # paire
        pts += 1
    elif row_count.count(1) == 5:
        if max(row) - min(row) == 4:
            if  is_Sorted(row):
                pts += 12 # suite sorted
            else:
                pts += 8 # suite
    return pts


def score_in_board(board):
    pts = 0
    for row in board:
        pts += score_in_row(row)

    pts += score_in_row(diagonal(board))
    return pts

def Score(board):
    #  for index, row in enumerate(board):
        #  board[index] = list(map(int, row))

    # rotation 90* pour calcul des col
    board2 = list(zip(*board[::-1]))
    return (score_in_board(board) + score_in_board(board2))
