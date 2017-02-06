from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# token authentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Game

# import the logging library
import logging

import json

logger = logging.getLogger('django')

class PlaySolo(APIView):
    """Start a solo game"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        """
        return token of game (for websockets)
        """
        gameObj = Game.objects.create()
        jsonDec = json.decoder.JSONDecoder()
        logger.info( jsonDec.decode (gameObj.game_set))
        return Response(gameObj.game_set,
                        status=status.HTTP_200_OK)




