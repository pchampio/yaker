from channels.generic.websockets import JsonWebsocketConsumer

from .tokenAuthWs import rest_auth
from .playsolo import *
from .playmulti import *

# Get channel_layer function
from channels.asgi import get_channel_layer

from channels.handler import AsgiRequest
from channels import Group

import logging
logger = logging.getLogger(__name__)

#  https://github.com/django/channels/blob/master/channels/generic/websockets.py
class ConsumerSolo(JsonWebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    channel_session_user = True

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform a game create on connection start"""

        GameSolo.create(message.user)
        message.channel_session["user"] = str(message.user.id)
        message.channel_session["username"] = str(message.user.username)

        # Accept connection
        message.reply_channel.send({"accept": True})

    def raw_receive(self, message, **kwargsself):
        """Called when a WebSocket frame is received."""
        try:
            self.receive(json.loads(message["text"]), message.channel_session["user"])
        except:
            logger.error("User " + message.channel_session["username"] +
                    ": Error :\nJson:\t" + message["text"])
            self.receive({}, message.channel_session["user"])

    def receive(self, content, user_id):
        """ GameSolo do the work """

        return_value, close = GameSolo.user_input(content, user_id)
        self.send(return_value)
        if close:
            self.close()
    # disconnect gerer par WebsocketConsumer


class ConsumerMultiLobby(JsonWebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    channel_session_user = True

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform a game create on connection start"""

        message.channel_session["user"] = str(message.user.id)
        message.channel_session["username"] = str(message.user.username)

        # get room name
        try:
            if "method" not in message.content:
                message.content["method"] = "FAKE"
            request = AsgiRequest(message)

        except Exception as e:
            raise ValueError("Cannot parse HTTP message - are you sure this is a HTTP consumer? %s" % e)

        room = request.GET.get("room")

        message.channel_session["room"] = room

        lobbyMsg = GameMultiLobby.newConsumerLobby(message.user,room)

        # Accept connection
        message.reply_channel.send({"accept": True})

        Group(room).add(message.reply_channel)

        group_user_send(self, message.channel_session["room"], lobbyMsg)

    def raw_receive(self, message, **kwargsself):
        """Called when a WebSocket frame is received."""
        try:
            self.receive(json.loads(message["text"]), message.channel_session)
        except:
            self.receive({}, message.channel_session)
            logger.error("User " + message.channel_session["username"] +
                    ": Error :\nJson:\t" + message["text"])

    def receive(self, content, channel_session):
        """ GameMultiLobby do the work """
        return_value = GameMultiLobby.user_input(content, channel_session)

        group_user_send(self, channel_session["room"], return_value)

    def raw_disconnect(self, message, **kwargs):
        return_value = GameMultiLobby.user_input({"leave":"1"}, message.channel_session)

        group_user_send(self, message.channel_session["room"], return_value)

        Group(message.channel_session["room"]).discard(message.reply_channel)

def group_user_send(user_chan, group_chan, data):
    """ gestion des sockets """
    if "user" in data:
        user_chan.send(data["user"])

    if "group" in data:
        #  Group(group_chan).send({"text": data["group"]})
        JsonWebsocketConsumer.group_send(group_chan,data["group"])

    if "group_close" in data and data["group_close"] == True:
        Group(group_chan).send({"close":True})

    if "user_close" in data and data["user_close"] == True:
        user_chan.close()
