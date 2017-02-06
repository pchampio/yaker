from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from .models import Followership

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


class FollowershipSerializer(serializers.ModelSerializer):
    """
    followers table
    """
    user = serializers.IntegerField(
        required=True,
    )

    follower = serializers.CharField(
        max_length=15,
        required=True,
    )

    def save(self):
        """
        Check if the followership DoesNotExist
        """

        user= User.objects.get(id=self.validated_data['user'])
        follower = User.objects.get(username=self.validated_data['follower'])

        follower_model = Followership(user=user, follower=follower)

        try:
            follower_model.save()

            new = {
                'type':'follower',
                'message': user.username + " is following you",
                'related': [user.username],
            }
            cache_w_add("user", follower.id, "notif", new, WEEK_IN_SEC * 2)

        except :
            logger.error("fail adding user to database or cache")
            return None
        return self

    def validate(self, data):
        """
        Check : Follower is a user (diffrent form follower adder), and not already your follower
        """
        try:
            follower = User.objects.exclude(id=data['user']).get(username=data['follower'])
            user = User.objects.get(id=data['user'])
        except User.DoesNotExist:
            raise serializers.ValidationError(data['follower'] + " is not a valid User")

        if Followership.objects.filter(user=user, follower=follower).exists():
            raise serializers.ValidationError(data['follower'] + " is already your follower")
        return data

    class Meta:
        model = Followership
        fields = ('user', 'follower')
