from channels.generic.websockets import JsonWebsocketConsumer

from .tokenAuthWs import rest_auth
from .gameManager import *

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
        message.channel_session['user'] = str(message.user.id)
        message.channel_session['username'] = str(message.user.username)

        # Accept connection
        message.reply_channel.send({"accept": True})

    def raw_receive(self, message, **kwargsself):
        """Called when a WebSocket frame is received."""
        try:
            self.receive(json.loads(message['text']), message.channel_session['user'])
        except:
            self.receive({}, message.channel_session['user'])
            logger.error("User " + message.channel_session['username'] +
                    ": Error parsing incoming json WebSocket:\nJson:\t" + message['text'])

    def receive(self, content, user_id):
        """ GameSolo do the work """

        return_value, close = GameSolo.user_input(content, user_id)
        self.send(return_value)
        if close:
            self.close()
    # disconnect gerer par WebsocketConsumer


from channels.handler import AsgiRequest
from channels import Group
class ConsumerMultiLobby(JsonWebsocketConsumer):

    # Doc : always guaranteed that connect will run before any receives
    #       (There’s a high cost to using enforce_ordering) ;(
    strict_ordering = True

    channel_session_user = True

    @rest_auth
    def connect(self, message, **kwargs):
        """Perform a game create on connection start"""

        message.channel_session['user'] = str(message.user.id)
        message.channel_session['username'] = str(message.user.username)

        try:
            if "method" not in message.content:
                message.content['method'] = "FAKE"
            request = AsgiRequest(message)

        except Exception as e:
            raise ValueError("Cannot parse HTTP message - are you sure this is a HTTP consumer? %s" % e)

        room = request.GET.get("room", None)

        message.channel_session['room'] = room

        lobbyMsg = GameMultiLobby.newLobby(message.user,room)

        # Accept connection
        message.reply_channel.send({"accept": True})

        Group(room).add(message.reply_channel)
        if 'user' in lobbyMsg:
            self.send(lobbyMsg['user'])

        if 'group' in lobbyMsg:
            Group(room).send({"text": lobbyMsg['group']})

    def raw_receive(self, message, **kwargsself):
        """Called when a WebSocket frame is received."""
        try:
            self.receive(json.loads(message['text']), message.channel_session)
        except:
            self.receive({}, message.channel_session)
            logger.error("User " + message.channel_session['username'] +
                    ": Error parsing incoming json WebSocket:\nJson:\t" + message['text'])

    def receive(self, content, channel_session):
        """ GameMultiLobby do the work """
        return_value, close = GameMultiLobby.user_input(content, channel_session)

        if 'user' in return_value:
            self.send(return_value['user'])

        if 'group' in return_value:
            Group(channel_session['room']).send({"text": return_value['group']})

        if close:
            Group(channel_session['room']).send({"close":True})
