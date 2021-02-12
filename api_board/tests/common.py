from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


def create_client_for_user():
    """
    Get user with role(user, admin, moderator) from fixtures,
    generate token for it and create authenticate client
    :return: Client
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
    """
    Return user from auth client
    """
    token_header = client._credentials['HTTP_AUTHORIZATION']
    token_str = token_header.split(' ')[-1]
    auth = JWTTokenUserAuthentication()
    valid_token = auth.get_validated_token(token_str)
    user = get_user_model().objects.get(id=valid_token.payload['user_id'])
    return user

