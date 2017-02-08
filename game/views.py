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
        return Response("cou",
                        status=status.HTTP_200_OK)
