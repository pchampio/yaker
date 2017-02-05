from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from .models import Friendship

# import the logging library
import logging

from .cache_wrapper import *



logger = logging.getLogger('django')

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This email is already in use.",
            )]
    )
    username = serializers.CharField(
        max_length=15,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This User is already in use.",
            )]
    )
    password = serializers.CharField(min_length=6, max_length=100,
                                     write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class FriendshipSerializer(serializers.ModelSerializer):
    """
    friends table
    """
    user = serializers.IntegerField(
        required=True,
    )

    friend = serializers.CharField(
        max_length=15,
        required=True,
    )

    def save(self):
        """
        Check if the friendship DoesNotExist
        """

        user= User.objects.get(id=self.validated_data['user'])
        friend = User.objects.get(username=self.validated_data['friend'])

        friend_model = Friendship(user=user, friend=friend)

        #  try:
        friend_model.save()

        new = {
            'type':'follower',
            'message': user.username + " is following you",
            'related': [user.username],
        }
        cache_w_add("user", friend.id, "notif", new, WEEK_IN_SEC * 2)

        #  except :
            #  logger.error("fail adding user to database or cache")
            #  return None
        return self

    def validate(self, data):
        """
        Check : Friend is a user (diffrent form friend adder), and not already your friend
        """
        try:
            friend = User.objects.exclude(id=data['user']).get(username=data['friend'])
            user = User.objects.get(id=data['user'])
        except User.DoesNotExist:
            raise serializers.ValidationError(data['friend'] + " is not a valid User")

        if Friendship.objects.filter(user=user, friend=friend).exists():
            raise serializers.ValidationError(data['friend'] + " is already your friend")
        return data

    class Meta:
        model = Friendship
        fields = ('user', 'friend')
