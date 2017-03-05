from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from .models import Followership

import logging
logger = logging.getLogger(__name__)

from .cache_wrapper import *


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

    # override default settings for password
    def create(self, validated_data):
            password = validated_data.pop('password', None)
            instance = self.Meta.model(**validated_data)
            if password is not None:
                instance.set_password(password)
            instance.save()
            return instance

    # override default settings for password
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

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

        user_id= self.validated_data['user']
        follower_name = self.validated_data['follower']


        try:

            follower_model = Followership()
            follower_model.save()
            #  http://stackoverflow.com/a/6996358
            follower_model.users.add(
                user_id,
                User.objects.get(username=follower_name).id
            )

            userName =  str(follower_model.users.get(id=user_id))
            followerId = follower_model.users.get(username=follower_name)

            new = {
                'type':'Follower',
                'message': userName + " is following you",
                'related': [userName],
            }
            cache_w_add("user", followerId, "notif", new, WEEK_IN_SEC * 2)

        except Exception as e:
            logger.error("fail adding user to database or cache" + e)
            return None
        return self

    def validate(self, data):
        """
        Check : Follower is a user (diffrent form follower adder), and not already your follower
        """
        try:
            if (Followership.objects
                    .filter(users__id=data['user'])
                    .filter(
                        users=User.objects.exclude(id=data['user']).get(username=data['follower'])
                    )
                    .filter(accepted=True)
                    .exists()):
                raise serializers.ValidationError(data['follower'] + " is already followed")
        except User.DoesNotExist:
            raise serializers.ValidationError(data['follower'] + " is not a valid User")

        return data

    class Meta:
        model = Followership
        fields = ('user', 'follower')
