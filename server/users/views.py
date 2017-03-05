from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# serializers
from users.serializers import UserSerializer
from users.serializers import FollowershipSerializer

# token authentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# models
from django.contrib.auth.models import User
from .models import Followership

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

class FollowershipVue(APIView):
    """
    Authentification is needed for this methods
    Add/get a follower to the current user
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        """
        add a follower to the current user
        """
        data = {}
        data['user'] = request.user.id
        if 'follower' in request.data:
            data['follower']=request.data['follower']
        logger.info(data)
        serializer = FollowershipSerializer(data=data)
        if serializer.is_valid():
            follower = serializer.save()
            if follower:
                detail_follower = serializer.data['follower']
                return Response({'detail': detail_follower + " is followered"},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        get a follower to the current user
        """
        followers_array = Followership.getFollowers(request.user)
        return Response({'followers' : followers_array},
                        status=status.HTTP_200_OK)

class FollowershipDell(APIView):
    """Delete a follower from a user"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format='json'):
        """
        add a follower to the current user
        """
        try:
            Followership.deleteFollower(request.user, request.data['follower'])
        except:
            return Response({'detail' : ["user not found in your follower list"]},
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

    def delete(self, request, id, format=None):
        cache_w_delete('user', request.user.id, 'notif', id)
        return Response(None,status=status.HTTP_200_OK)

