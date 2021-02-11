from pathlib import Path

from django.core import exceptions
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_board.models import User
from api_board.tests.common import create_client_for_user


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent/'fixtures', ])
class TestUser(TestCase):
    fixtures = ['users']
    username = User.objects.last().username
    list_url = reverse('user-list')
    detail_url = reverse('user-detail', kwargs={'username': username})
    detail_url_invalid = reverse('user-detail', kwargs={'username': 'Joe'})
    current_user_url = reverse('user-me')
    data = {
        'username': 'test_user',
        'email': 'testuser@mail.com',
        'first_name': 'Test',
        'last_name': 'User',
        'bio': 'Created for tests',
        'role': 'moderator'
    }
    new_data = {'first_name': 'Updated name'}

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_client_for_user()
        cls.not_auth_client = APIClient()
        super().setUpTestData()

    def test_user_list_pagination(self):
        response = self.admin_client.get(self.list_url)
        self.assertEqual(response.data.get('count'), User.objects.count())
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)

    def test_user_list_response_data(self):
        response = self.admin_client.get(self.list_url)
        data = response.json()['results'][0]
        user = User.objects.get(username=data['username'])
        self.check_response_data(data, user)

    def test_user_list_filter(self):
        param = 'user'
        url = self.list_url + '?search=%s' % param
        response = self.admin_client.get(url)
        users = User.objects.filter(username__icontains=param)
        self.assertEqual(response.data['count'], users.count())

    def test_user_list_permissions(self):
        response = self.admin_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_permissions(method='get', url=self.list_url)

    def test_create_user_valid_data(self):
        response = self.admin_client.post(self.list_url, data=self.data)
        self.assertDictEqual(response.json(), self.data)

    def test_create_user_invalid_data(self):
        data = {}
        response = self.admin_client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_permissions(self):
        response = self.admin_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_permissions(method='post', url=self.list_url, data=self.data)

    def test_get_user_response_data(self):
        response = self.admin_client.get(self.detail_url)
        user = User.objects.get(username=self.username)
        self.check_response_data(response.json(), user)

    def test_get_user_invalid_path(self):
        response = self.admin_client.get(self.detail_url_invalid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_permissions(self):
        response = self.admin_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_permissions(method='get', url=self.detail_url)

    def test_patch_user_response_data(self):
        response = self.admin_client.patch(self.detail_url, data=self.new_data)
        user = User.objects.get(username=self.username)
        self.check_response_data(response.json(), user)

    def test_patch_user_invalid_path(self):
        response = self.admin_client.patch(self.detail_url_invalid,
                                           data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_permissions(self):
        response = self.admin_client.patch(self.detail_url, data=self.new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_permissions(method='put', url=self.detail_url, data=self.new_data)

    def test_delete_user_permissions(self):
        self.check_permissions(method='delete', url=self.detail_url)

    def test_delete_user_invalid_path(self):
        response = self.admin_client.delete(self.detail_url_invalid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_valid_path(self):
        response = self.admin_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(exceptions.ObjectDoesNotExist):
            User.objects.get(username=self.username)

    def test_get_current_user_response_data(self):
        response = self.user_client.get(self.current_user_url)
        user = response.wsgi_request.user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_response_data(response.json(), user)

    def test_get_current_user_for_not_auth_user(self):
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_current_user(self):
        response = self.user_client.patch(self.current_user_url, data={'bio': 'About'})
        user = response.wsgi_request.user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_response_data(response.json(), user)

    def check_permissions(self, method, url, data=None):
        """
        Check permissions for various url and methods.
        """
        user_method = getattr(self.user_client, method)
        response = user_method(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        moderator_method = getattr(self.user_client, method)
        response = moderator_method(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        not_auth_user_method = getattr(self.not_auth_client, method)
        response = not_auth_user_method(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def check_response_data(self, data, user):
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['bio'], user.bio)
        self.assertEqual(data['role'], user.role)
