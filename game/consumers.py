from channels import Group
from channels.sessions import channel_session
from .auth_token_mixin import *

from channels.generic.websockets import WebsocketConsumer
from .cache_wrapper import *

from .models import Game, Save

#  https://github.com/django/channels/blob/master/channels/generic/websockets.py
class MyConsumer(WebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    def connection_groups(self, **kwargs):
        """Called to return the list of groups to automatically add/remove this connection to/from."""
        return ["test"]

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform things on connection start"""

        cachedGame = cache_w_gets("user", message.user.id, "sologame")
        if not cachedGame:
            gameSession = Game.get_or_create(message.user)
            sologame = {}
            sologame['game_id'] = gameSession.id
            sologame['game_set'] = gameSession.game_set
            sologame['user_board'] = [[0]*5 for _ in range(5)]
            sologame['user_board'][1][1] = 1
            sologame['index_set'] = 0
            sologame['user_id'] = message.user.id
            cache_w_add("user", message.user.id, "sologame", sologame, WEEK_IN_SEC * 2)
            cachedGame = sologame

        logger.info(cachedGame)

        message.channel_session['user'] = str(message.user.id)

        # Accept connection
        message.reply_channel.send({"accept": True})
        # Work out room name from path (ignore slashes)
        #  room = message.content['path'].strip("/")
        room = "test"
        # Save room in session and add us to the group
        message.channel_session['room'] = room

        Group("chat-%s" % room).add(message.reply_channel)

    def raw_receive(self, message, **kwargs):
        """Called when a WebSocket frame is received."""

        Group("chat-%s" % message.channel_session['room']).send({
            "text": message['text'] + " " + message.channel_session['user'],
        })



"""

// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers
socket = new WebSocket("ws://" + window.location.host + "/playsolo/?token=26325c8b4d0d94ab28a289a0fc7b20999aa6e62d");
socket.onmessage = function(e) {
    console.log(e.data);
}
socket.onopen = function() {
    socket.send("hello world");
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

"""
