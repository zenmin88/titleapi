from pathlib import Path

from django.core import exceptions
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_board.models import Title, Category, Genre
from api_board.tests.common import create_client_for_user


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent/'fixtures', ])
class TestTitle(TestCase):
    fixtures = ['genres', 'categories', 'titles', 'users']

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_client_for_user()
        cls.not_auth_client = APIClient()

        cls.list_url = reverse('title-list')
        cls.pk = Title.objects.first().id
        cls.detail_url = reverse('title-detail', kwargs={'pk': cls.pk})

        category = Category.objects.get(slug='film')
        genre1 = Genre.objects.get(slug='comedy')
        genre2 = Genre.objects.get(slug='family')
        cls.data = {
            'name': 'Home alone 3',
            'year': 1997,
            'category': category.slug,
            'genre': [genre1.slug, genre2.slug],
            'description': 'failed movie'
        }
        cls.new_data = {'name': 'Updated name'}
        super().setUpTestData()

    def test_title_list_not_auth_user(self):
        response = self.not_auth_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_title_list_pagination(self):
        response = self.not_auth_client.get(self.list_url)
        self.assertEqual(response.data.get('count'), Title.objects.count())
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)

    def test_title_list_response_data(self):
        response = self.not_auth_client.get(self.list_url)
        data = response.json()['results'][0]
        self.check_response_data(data)

    def test_title_list_filter_by_name(self):
        param = 'home'
        url = self.list_url + '?name=%s' % param
        response = self.not_auth_client.get(url)
        titles = Title.objects.filter(name__icontains=param)
        self.assertEqual(response.data['count'], titles.count())

    def test_title_list_filter_by_year(self):
        param = 1990
        url = self.list_url + '?year=%s' % param
        response = self.not_auth_client.get(url)
        titles = Title.objects.filter(year=param)
        self.assertEqual(response.data['count'], titles.count())

    def test_title_list_filter_by_category(self):
        category_slug = 'film'
        url = self.list_url + '?category=%s' % category_slug
        response = self.not_auth_client.get(url)
        titles = Title.objects.filter(category__slug=category_slug)
        self.assertEqual(response.data['count'], titles.count())

    def test_title_list_filter_by_genre(self):
        genre_slug = 'comedy'
        url = self.list_url + '?genre=%s' % genre_slug
        response = self.not_auth_client.get(url)
        titles = Title.objects.filter(genre__slug=genre_slug)
        self.assertEqual(response.data['count'], titles.count())

    def test_create_title_by_admin_valid_data(self):
        response = self.admin_client.post(self.list_url, data=self.data)
        self.data['id'] = Title.objects.last().id
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), self.data)
        self.data.pop('id')

    def test_create_title_by_admin_invalid_data(self):
        data = {}
        response = self.admin_client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Required field
        required_fields = ('name', 'year', 'category')
        for required_field in required_fields:
            self.assertIn(required_field, response.data)

    def test_create_title_by_not_auth_user(self):
        response = self.not_auth_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_title_by_moderator(self):
        response = self.moderator_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_title_by_user(self):
        response = self.user_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_title_not_auth_user(self):
        response = self.not_auth_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_response_data(response.data)

    def test_get_title_invalid_path(self):
        url = reverse('title-detail', kwargs={'pk': 181})
        response = self.not_auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_title_valid_data(self):
        response = self.admin_client.patch(self.detail_url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.new_data['name'])

    def test_update_title_invalid_data(self):
        data = {'genre': ''}
        response = self.admin_client.patch(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_title_by_not_auth_user(self):
        response = self.not_auth_client.patch(self.detail_url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_title_by_moderator(self):
        response = self.moderator_client.patch(self.detail_url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_title_by_user(self):
        response = self.user_client.patch(self.detail_url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_title_invalid_path(self):
        url = reverse('title-detail', kwargs={'pk': 181})
        response = self.admin_client.patch(url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_title_invalid_path(self):
        url = reverse('title-detail', kwargs={'pk': 181})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_title_by_user(self):
        response = self.user_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_title_by_moderator(self):
        response = self.moderator_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_title_by_not_auth_user(self):
        response = self.not_auth_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_allow_method_title(self):
        response = self.admin_client.put(self.detail_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_title_by_admin(self):
        response = self.admin_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Title.objects.get(id=self.pk)
        with self.assertRaises(exceptions.ObjectDoesNotExist):
            Title.objects.get(id=self.pk)

    def check_response_data(self, data):
        params = ('category', 'description', 'genre', 'id', 'name', 'rating', 'year')
        for param in params:
            self.assertIn(param, data)
        self.assertIn('name', data['category'])
        self.assertIn('slug', data['category'])
        self.assertIn('name', data['genre'][0])
        self.assertIn('slug', data['genre'][0])
        self.assertIsInstance(data['category'], dict)
        self.assertIsInstance(data['genre'], list)
