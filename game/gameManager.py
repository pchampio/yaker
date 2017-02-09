from django.core.cache import cache

class GameManger():
    """ gère le jeux """

    def create(user_id):
        key = 'user:'+str(user_id)+':sologame'
        if key in cache:
            cachedGame = cache.get(key)
        else:
            gameSession = Game.get_or_create(message.user)
            sologame = {}
            sologame['game_id'] = gameSession.id
            sologame['game_set'] = gameSession.game_set
            sologame['user_board'] = [[0]*5 for _ in range(5)]
            sologame['index_set'] = 0
            sologame['user_id'] = message.user.id
            cache.set(key, sologame, 120)
            cachedGame = sologame

    def user_input(content, user_id):
        """ check if user is malicious (or just a dev) and give next value of board """

