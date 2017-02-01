from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import UserSerializer
from accounts.serializers import FriendshipSerializer
from rest_framework.authtoken.models import Token

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from .models import Friendship
#  There is Q objects that allow to complex lookups. or in filter
from django.db.models import Q

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
        if 'user' in data:
            del data['user']
        data['user'] = request.user.id
        if 'friend' in request.data:
            data['friend']=request.data['friend']
        logger.info(data)
        serializer = FriendshipSerializer(data=data)
        if serializer.is_valid():
            try:
                user = User.objects.exclude(id=data['user']).get(username=data['friend'])
            except User.DoesNotExist:
                return Response({'detail' : data['friend'] + " is not a valid friend" }, status=status.HTTP_400_BAD_REQUEST)

            friend = serializer.save()
            if friend:
                detail_friend = serializer.data['friend']
                return Response({'detail': detail_friend + " is now your firend"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': data["friend"] + " is already your friend"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        get a friend to the current user
        """
        try:
            user = User.objects.get(id=request.user.id)
            friends = Friendship.objects.filter(Q(user=request.user) | Q(friend=request.user))
            friends_array = []
            for e in friends:
                friends_array.append(e.friend.username)
                friends_array.append(e.user.username)
            friends_array.uni
            friends_array = filter(lambda a: a != request.user.username,friends_array)
            logger.info(friends_array)
        except Friendship.DoesNotExist:
            return Response({'detail' : "you have no friend"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'friends' : friends_array}, status=status.HTTP_400_BAD_REQUEST)


class AuthUser(APIView):

    """Authentification is needed for this methods"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        logger.info(request.user)
        logger.info(Token.objects.get(user=request.user))

        return Response({'username': request.user.username})
