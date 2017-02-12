from channels.generic.websockets import JsonWebsocketConsumer

from .tokenAuthWs import *
from .gameManager import *

import logging
logger = logging.getLogger(__name__)

#  https://github.com/django/channels/blob/master/channels/generic/websockets.py
class MyConsumer(JsonWebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    channel_session_user = True

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform a game create on connection start"""

        GameManger.create(message.user)
        message.channel_session['user'] = str(message.user.id)

        # Accept connection
        message.reply_channel.send({"accept": True})


    def raw_receive(self, message, **kwargsself):
        """Called when a WebSocket frame is received."""
        try:
            self.receive(json.loads(message['text']), message.channel_session['user'])
        except:
            self.receive({}, message.channel_session['user'])
            logger.error("Error parsing incoming json WebSocket")

    def receive(self, content, user_id):
        """ GameManger do the work """

        return_value, close = GameManger.user_input(content, user_id)
        self.send(return_value)
        if close:
            self.close()


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
