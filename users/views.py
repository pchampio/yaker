from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# serializers
from users.serializers import UserSerializer
from users.serializers import FriendshipSerializer

# token authentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# models
from django.contrib.auth.models import User
from .models import Friendship

#  There is Q objects that allow to complex lookups. or in filter
from django.db.models import Q

from .cache_wrapper import *

# import the logging library
import logging

logger = logging.getLogger('django')

class CreateUser(APIView):
    """
    Creates the user.
    """

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                del json['id']
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendshipVue(APIView):
    """
    Authentification is needed for this methods
    Add/get a friend to the current user
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        """
        add a friend to the current user
        """
        data = {}
        data['user'] = request.user.id
        if 'friend' in request.data:
            data['friend']=request.data['friend']
        logger.info(data)
        serializer = FriendshipSerializer(data=data)
        if serializer.is_valid():
            friend = serializer.save()
            if friend:
                detail_friend = serializer.data['friend']
                return Response({'detail': detail_friend + " is now your firend"},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        get a friend to the current user
        """
        try:
            friends = (Friendship.objects.filter(user=request.user))
            friends_array = [ x.friend.username  for x in friends ]
            friends_array = filter(lambda a: a != request.user.username,friends_array)
        except Friendship.DoesNotExist:
            return Response({'detail' : "database error"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'friends' : friends_array},
                        status=status.HTTP_200_OK)

class FriendshipDell(APIView):
    """Delete a friend from a user"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        """
        add a friend to the current user
        """
        try:
            friend = (Friendship.objects.get(user=request.user,
                                             friend=User.objects.get(
                                                 username=request.data['friend'])))
            friend.delete()
        except:
            return Response({'detail' : ["user not found in your friend list"]},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)



class Login(APIView):
    """Log a user in return the user related token"""

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        token = Token.objects.get(user=request.user)
        return Response({"token": token.key} )

class AuthUser(APIView):

    """Authentification is needed for this methods"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        response = {'username': request.user.username}
        response['notif'] = cache_w_gets('user', request.user.id, 'notif')

        return Response(response,status=status.HTTP_200_OK)
