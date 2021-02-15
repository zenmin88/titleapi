from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


def create_clients_for_users():
    """Return clients for users with roles: user, moderator, administrator.

    :return: (user_client, moderator_client, admin_client), Authorized client for user with role admin,
    Authorized client for user with role moderator, Authorized client for user with role user
    """
    user = get_user_model().objects.get(username='user', role='user')
    moderator = get_user_model().objects.get(username='moderator', role='moderator')
    admin = get_user_model().objects.get(username='admin', role='admin')

    user_token = RefreshToken.for_user(user)
    user_client = APIClient()
    moderator_token = RefreshToken.for_user(moderator)
    moderator_client = APIClient()
    admin_token = RefreshToken.for_user(admin)
    admin_client = APIClient()

    user_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(user_token.access_token))
    moderator_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(moderator_token.access_token))
    admin_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(admin_token.access_token))

    return user_client, moderator_client, admin_client


def get_user_from_client(client):
    """Return object of user from authorized client."""
    token_header = client._credentials['HTTP_AUTHORIZATION']
    token_str = token_header.split(' ')[-1]
    auth = JWTTokenUserAuthentication()
    valid_token = auth.get_validated_token(token_str)
    user = get_user_model().objects.get(id=valid_token.payload['user_id'])
    return user


def create_client_for_user():
    """Create user with role=user, return client for it."""
    other_user = get_user_model().objects.create(username='other_user', email='mail@mail.com')
    token = RefreshToken.for_user(other_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    return client
