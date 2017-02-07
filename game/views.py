from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# token authentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Game

from json import loads, dumps

# import the logging library
import logging
logger = logging.getLogger('django')



class PlaySolo(APIView):
    """Start a solo game"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        """
        return token of game (for websockets)
        """

        Game.get_or_create(request.user)


        return Response("cou",
                        status=status.HTTP_200_OK)


from channels import Group
from channels.sessions import channel_session
from .auth_token_mixin import *

# Connected to websocket.connect
@channel_session
@rest_auth
def ws_connect(message):

    logger.info(message.user)
    logger.info(message.auth)
    message.channel_session['user'] = str(message.user)

    # Accept connection
    message.reply_channel.send({"accept": True})
    # Work out room name from path (ignore slashes)
    room = message.content['path'].strip("/")
    # Save room in session and add us to the group
    message.channel_session['room'] = room

    Group("chat-%s" % room).add(message.reply_channel)

# Connected to websocket.receive
@channel_session
def ws_message(message):

    Group("chat-%s" % message.channel_session['room']).send({
        "text": message['text'] + " " + message.channel_session['user'],
    })

# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['room']).discard(message.reply_channel)

#  // Note that the path doesn't matter for routing; any WebSocket
#  // connection gets bumped over to WebSocket consumers
#  socket = new WebSocket("ws://" + window.location.host + "/chat/?token=26325c8b4d0d94ab28a289a0fc7b20999aa6e62d");
#  socket.onmessage = function(e) {
    #  console.log(e.data);
#  }
#  socket.onopen = function() {
    #  socket.send("hello world");
#  }
#  // Call onopen directly if socket is already open
#  if (socket.readyState == WebSocket.OPEN) socket.onopen();
