from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient


from api_board.models import Genre


def create_genres(*genres):
    for genre in genres:
        Genre.objects.create(**genre)

def get_genre_detail_url(data):
    genre = Genre.objects.create(**data)
    url = reverse('genre-detail', kwargs={'slug': genre.slug})
    return url


def create_client_for_user(role='user'):
    data = {
        "username": role,
        "email": role +"@gmail.com",
        "role": role
    }
    user = get_user_model().objects.create_user(**data)
    user_token = RefreshToken.for_user(user)
    user_client = APIClient()
    user_client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(user_token.access_token))

    return user_client
