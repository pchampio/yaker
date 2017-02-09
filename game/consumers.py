from django.core.serializers.json import DjangoJSONEncoder, json
from channels import Group
from channels.sessions import channel_session
from .tokenAuthWs import *

from channels.generic.websockets import JsonWebsocketConsumer
from django.core.cache import cache

from .gameManager import *

from .models import Game, Save
from users.models import Followership
from django.contrib.auth.models import User


#  https://github.com/django/channels/blob/master/channels/generic/websockets.py
class MyConsumer(JsonWebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform things on connection start"""

        #  key = 'user:'+str(message.user.id)+':sologame'
        #  if key in cache:
            #  cachedGame = cache.get(key)
        #  else:
            #  gameSession = Game.get_or_create(message.user)
            #  sologame = {}
            #  sologame['game_id'] = gameSession.id
            #  sologame['game_set'] = gameSession.game_set
            #  sologame['user_board'] = [[0]*5 for _ in range(5)]
            #  sologame['index_set'] = 0
            #  sologame['user_id'] = message.user.id
            #  cache.set(key, sologame, 120)
            #  cachedGame = sologame

        GameManager.create(message.user.id)

        message.channel_session['user'] = str(message.user.id)

        # Accept connection
        message.reply_channel.send({"accept": True})



    def raw_receive(self, message, **kwargs):
        """Called when a WebSocket frame is received."""

        if "text" in message:
            self.receive(json.loads(message['text']), message.channel_session['user'])
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    def receive(self, content, user_id):
        jsonDec = json.decoder.JSONDecoder()

        key = 'user:'+user_id+':sologame'
        game = cache.get(key)
        board = jsonDec.decode(game['game_set'])

        logger.info(game)


        if game['index_set'] >= 24:
            user = User.objects.get(id=user_id)
            game_save = Game.objects.get(id=game['game_id'])
            game_board = json.dumps(game['user_board'])
            # save in Database
            Save.objects.create(user=user, game=game_save, score=1, game_board=game_board)
            # delete from cache
            cache.delete(key)

            # scores

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

            self.send(
                {"score":"score = 1",
                 "world_first":firsts,
                 "followers_best":firsts_followers
                 }, True # close ws
            )
            return

        if "i" in content and 'j' in content and 'value' in content:
            if content['i'].isdigit() and content['j'].isdigit() and content['value'].isdigit():
                i = int(content['i'])
                j = int(content['j'])
                if 0 <= i < 5 and 0 <= j < 5 and int(content['value']) == board[game['index_set']]:
                    if game['user_board'][i][j] == 0:
                        game['user_board'][i][j] = content['value']
                        game['index_set'] += 1
                        self.send(
                            {"dice": board[game['index_set']]}
                        )
                        cache.set(key, game, 604800 * 2) # 2 week
                        return

        self.send({"dice":board[game['index_set']], "error":"did you try to fool me"})


    # disconnect gerer par WebsocketConsumer


"""

// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers
socket = new WebSocket("ws://" + window.location.host + "/playsolo/?token=26325c8b4d0d94ab28a289a0fc7b20999aa6e62d");
socket.onmessage = function(e) {
    console.log(e.data);
}
socket.onopen = function() {
    socket.send(JSON.stringify({
  id: "client1"
}));
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();


socket.send(JSON.stringify({
  i: "3", j:"4", value: "6"
}))

"""
