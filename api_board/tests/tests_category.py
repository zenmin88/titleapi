from pathlib import Path

from django.core import exceptions
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_board.models import Category
from api_board.tests.common import create_clients_for_users


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent/'fixtures', ])
class TestCategory(TestCase):
    fixtures = ['categories', 'users']
    list_url = reverse('category-list')
    data = {"name": "Western",
            "slug": "western"}

    slug = Category.objects.first().slug
    detail_url = reverse('category-detail', kwargs={'slug': slug})

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_clients_for_users()
        cls.not_auth_client = APIClient()

        super().setUpTestData()

    def test_get_category_list_for_not_auth_user(self):
        response = self.not_auth_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_category_list_pagination(self):
        response = self.not_auth_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(response.data.get('count'), Category.objects.count())

    def test_get_category_list_response_data(self):
        self.admin_client.post(self.list_url, data=self.data)
        response = self.not_auth_client.get(self.list_url)
        data = response.data['results'][-1]
        self.assertEqual(data['slug'], self.data['slug'])

    def test_create_category_without_slug(self):
        response = self.admin_client.post(self.list_url, data={"name": "horror"})
        category = Category.objects.last()
        self.assertEqual(response.data['slug'], category.slug)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_by_auth_user(self):
        response = self.user_client.post(self.list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_by_not_auth_user(self):
        response = self.not_auth_client.post(self.list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_by_admin(self):
        response = self.admin_client.post(self.list_url, self.data)
        category = Category.objects.last()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['slug'], category.slug)

    def test_create_category_by_moderator(self):
        response = self.moderator_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, 403)

    def test_filter_by_category_name(self):
        param = 'book'
        url = self.list_url + '?search=%s' % param
        response = self.admin_client.get(url)
        queryset = Category.objects.filter(name__icontains=param)
        self.assertEqual(response.data['count'], queryset.count())

    def test_delete_category_by_moderator(self):
        response = self.moderator_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_by_user(self):
        response = self.user_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_by_not_auth_user(self):
        response = self.not_auth_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_by_admin(self):
        response = self.admin_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(exceptions.ObjectDoesNotExist):
            Category.objects.get(slug=self.slug)
