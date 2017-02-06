        #  sys.stderr.write(repr(response.data) + '\n')
from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .views import AuthUser

import sys
from django.test import  override_settings
@override_settings(CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/4",
            'TIMEOUT': None,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            }
        }
    })
class AccountsTest(APITestCase):
    def setUp(self):

        # URL for creating an account.
        self.create_url = reverse('account-create')

        # URL for the auth-view
        self.auth_url = reverse('auth-view')

        # URL for the adding follower
        self.follower_add = reverse('follower-add')

        # URL for the deleting follower
        self.follower_delete = reverse('follower-delete')

        # URL for the deleting follower
        self.follower_list = reverse('follower-list')

        # URL for the login
        self.login = reverse('login')

        self.test_data = {
            'username': 'pierre',
            'email': 'pierre@champion.fr',
            'password': 'hkjl'*3
        }

        # response test
        self.test_response = self.client.post(self.create_url , self.test_data, format='json')

    #  def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushdb()

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }

        response = self.client.post(self.create_url , data, format='json')
        user = User.objects.latest('id')
        token = Token.objects.get(user=user)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['token'], token.key)
        self.assertFalse('password' in response.data)


    def test_create_user_with_short_password(self):
        """
        Ensures user is not created for password lengths less than 8.
        """

        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': 'foo'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_no_password(self):
        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': ''
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_too_long_username(self):
        data = {
            'username': 'foo'*30,
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_no_username(self):
        data = {
            'username': '',
            'email': 'foobarbaz@example.com',
            'password': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_preexisting_username(self):
        data = {
            'username': self.test_data['username'],
            'email': 'sefsdf@sdfsd.fr',
            'password': 'testuser'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': 'testuser2',
            'email': self.test_data['email'],
            'password': 'testuser'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_invalid_email(self):
        data = {
            'username': 'foobarbaz',
            'email':  'testing',
            'passsword': 'foobarbaz'
        }


        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_no_email(self):
        data = {
            'username' : 'foobar',
            'email': '',
            'password': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)


    def test_auth_view(self):
        """
        Ensure we can Retrieve from token
        """

        view = AuthUser.as_view()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_response.data['token'])

        response = client.get(self.auth_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.test_response.data['username'])

        client.logout()

    def test_login(self):
        """
        Ensure we can login
        """

        view = AuthUser.as_view()

        client = APIClient()
        user = User.objects.latest('id')

        user = User.objects.latest('id')
        token = Token.objects.get(user=user)

        client.force_authenticate(user=user)

        response = client.get(self.login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['token'], token.key)

        client.logout()

    def test_add_delete_follower(self):

        data = {'username': 'foobar','email': 'foobar@example.com','password': 'somepassword'}

        follower_response = self.client.post(self.create_url , data, format='json')

        view = AuthUser.as_view()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_response.data['token'])

        # add
        response = client.post(self.follower_add, {"follower": data['username']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # delete
        response = client.post(self.follower_delete, {"follower": data['username']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.logout()


    def test_notif_follower(self):

        data = {'username': 'foobar','email': 'foobar@example.com','password': 'somepassword'}

        follower_response = self.client.post(self.create_url , data, format='json')


        user = User.objects.latest('id')
        token = Token.objects.get(user=user)


        view = AuthUser.as_view()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_response.data['token'])

        # add
        response = client.post(self.follower_add, {"follower": data['username']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        client.logout()

        view = AuthUser.as_view()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get(self.auth_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #  sys.stderr.write(repr(response.data) + '\n')
        self.assertEqual(response.data['notif'][0]['type'], 'follower')
        self.assertEqual(response.data['notif'][0]['message'], 'pierre is following you')
        self.assertEqual(response.data['notif'][0]['related'], ['pierre'])



    def test_add_invalid_follower(self):

        view = AuthUser.as_view()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_response.data['token'])

        # add
        response = client.post(self.follower_add, {"follower": "nopeUser"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        client.logout()

    def test_delete_invalid_follower(self):

        view = AuthUser.as_view()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_response.data['token'])

        # delete
        response = client.post(self.follower_delete, {"follower": "nopeUser"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        client.logout()


    def test_auth_view_fail(self):
        """
        Ensure we can fail when no token provided
        """
        response = self.client.get(self.auth_url)
        self.assertEqual(response.status_code, 401)

