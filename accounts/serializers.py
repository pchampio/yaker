from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from .models import Friendship

# import the logging library
import logging

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
        user_id = self.validated_data['user']
        user= User.objects.get(id=user_id)

        friend_name = self.validated_data['friend']
        friend = User.objects.get(username=friend_name)

        friend_model = Friendship(user=user, friend=friend)
        try:
            friend_model.save()
        except:
            return None
        return self

    class Meta:
        model = Friendship
        fields = ('user', 'friend')
