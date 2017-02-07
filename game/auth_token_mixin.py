import functools

from channels.handler import AsgiRequest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.settings import api_settings

import logging
logger = logging.getLogger('django')


authenticators = [auth() for auth in api_settings.DEFAULT_AUTHENTICATION_CLASSES]

#  stolen from :
    #  https://github.com/abarto/shared_canvas_channels/blob/master/shared_canvas_channels/shared_canvas/jwt_decorators.py
    #  https://github.com/abarto/shared_canvas_channels/blob/master/shared_canvas_channels/shared_canvas/jwt_decorators.py

    # and https://github.com/django/channels/issues/510 (issue closed 11 days ago sooo lucky)

def rest_auth(func):
    """
    Wraps a HTTP or WebSocket connect consumer (or any consumer of messages
    that provides a "cookies" or "get" attribute) to provide a "http_session"
    attribute that behaves like request.session; that is, it's hung off of
    a per-user session key that is saved in a cookie or passed as the
    "session_key" GET parameter.
    It won't automatically create and set a session cookie for users who
    don't have one - that's what SessionMiddleware is for, this is a simpler
    read-only version for more low-level code.
    If a message does not have a session we can inflate, the "session" attribute
    will be None, rather than an empty session you can write to.
    Does not allow a new session to be set; that must be done via a view. This
    is only an accessor for any existing session.
    """

    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        # Make sure there's NOT a http_session already
        try:
            # We want to parse the WebSocket (or similar HTTP-lite) message
            # to get cookies and GET, but we need to add in a few things that
            # might not have been there.
            if "method" not in message.content:
                message.content['method'] = "FAKE"
            request = AsgiRequest(message)

        except Exception as e:
            raise ValueError("Cannot parse HTTP message - are you sure this is a HTTP consumer? %s" % e)
        # Make sure there's a session key
        user = None
        auth = None
        auth_token = request.GET.get("token", None)

        if auth_token:
            # comptatibility with rest framework
            request._request = {}
            request.META["HTTP_AUTHORIZATION"] = "token {}".format(auth_token)
            for authenticator in authenticators:
                try:
                    user_auth_tuple = authenticator.authenticate(request)
                except AuthenticationFailed:
                    pass

                if user_auth_tuple is not None:
                    message._authenticator = authenticator
                    user, auth = user_auth_tuple
                    break
        message.user, message.auth = user, auth

        if message.user is None:
            message.reply_channel.send({'close': True})
            raise ValueError("Missing token field. Closing channel.")

        # Make sure there's a session key
        # Run the consumer
        result = func(message, *args, **kwargs)
        return result
    return inner

