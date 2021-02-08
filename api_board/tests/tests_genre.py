from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from api_board.models import Genre
from api_board.tests.common import create_genres, create_client_for_user,get_genre_detail_url


class TestGenre(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin_client = create_client_for_user(role='admin')
        cls.moderator_client = create_client_for_user(role='moderator')
        cls.user_client = create_client_for_user(role='user')
        cls.not_auth_client = APIClient()

        cls.url = reverse('genre-list')
        cls.data = {"name": "horror",
                    "slug": "detective"}
        cls.data1 = {'name': 'fantasy',
                     'slug': 'fantasy'}
        super().setUpClass()

    def test_get_genre_list_for_not_auth_user(self):
        response = self.not_auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_genre_without_slug(self):
        response = self.admin_client.post(self.url, data=self.data)
        self.assertTrue(response.data.get('slug'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_genre_by_auth_user(self):
        response = self.user_client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_genre_by_not_auth_user(self):
        response = self.not_auth_client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_genre_by_admin(self):
        response = self.admin_client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 1)

    def test_create_genre_by_moderator(self):
        response = self.moderator_client.post(self.url, data={"name": "horror"})
        self.assertEqual(response.status_code, 403)

    def test_genre_list_pagination(self):
        create_genres(self.data, self.data1)
        response = self.admin_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data.get('count'), 2)

    def test_filter_by_genre_name(self):
        create_genres(self.data, self.data1)
        url = self.url + '?search=horror'
        response = self.admin_client.get(url)
        response_data = response.json()
        self.assertEqual(len(response_data.get('results')), 1)
        self.assertEqual(self.data, response_data.get('results')[0])

    def test_delete_genre_by_admin(self):
        url = get_genre_detail_url(self.data)
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_genre_by_moderator(self):
        url = get_genre_detail_url(self.data)
        response = self.moderator_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_genre_by_user(self):
        url = get_genre_detail_url(self.data)
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_genre_by_not_auth_user(self):
        url = get_genre_detail_url(self.data)
        response = self.not_auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)






