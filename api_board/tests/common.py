from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def create_client_for_user():

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
