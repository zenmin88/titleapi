from pathlib import Path

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_board.models import Comment
from api_board.tests.common import create_clients_for_users, get_user_from_client, create_client_for_user


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent/'fixtures', ])
class TestComment(TestCase):
    fixtures = ['reviews', 'titles', 'categories', 'users', 'genres', 'comments']
    title_id = 1
    review_id = 1
    comment_id = 1
    list_url = reverse('comment-list', kwargs={'title_id': title_id,
                                               'review_id': review_id})

    detail_url = reverse('comment-detail', kwargs={'title_id': title_id,
                                                   'review_id': review_id,
                                                   'pk': comment_id})
    data = {'text': 'New comment'}

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_clients_for_users()
        cls.not_auth_client = APIClient()
        super().setUpTestData()

    def test_comment_list_pagination(self):
        response = self.user_client.get(self.list_url)
        self.assertEqual(response.data.get('count'), Comment.objects.count())
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)

    def test_comment_list_response_data(self):
        response = self.not_auth_client.get(self.list_url)
        data = response.json()['results'][0]
        comment = Comment.objects.get(id=data['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_response_data(data, comment)

    def check_response_data(self, data, comment):
        self.assertEqual(data['id'], comment.id)
        self.assertEqual(data['author'], comment.author.username)
        self.assertEqual(data['text'], comment.text)

    def test_comment_list_invalid_path(self):
        url = reverse('comment-list', kwargs={'title_id': self.title_id,
                                              'review_id': 35})
        response = self.not_auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment(self):
        response = self.user_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_from_client(self.user_client)
        self.assertEqual(response.data['text'], self.data['text'])
        self.assertEqual(response.data['author'], user.username)
        comment = Comment.objects.last()
        self.check_response_data(response.data, comment)

    def test_create_comment_invalid_data(self):
        data = {}
        response = self.user_client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_create_comment_not_auth_user(self):
        response = self.not_auth_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_comment(self):
        response = self.not_auth_client.get(self.detail_url)
        comment = Comment.objects.get(id=self.comment_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_response_data(response.data, comment)

    def test_get_comment_invalid_path(self):
        detail_url = reverse('comment-detail', kwargs={'title_id': self.title_id,
                                                       'review_id': self.review_id,
                                                       'pk': 35})
        response = self.not_auth_client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent / 'fixtures', ])
class TestCommentUpdateDelete(TestCase):
    fixtures = ['titles', 'categories', 'users', 'genres', 'reviews']
    title_id = 1
    review_id = 1
    comment_id = 1
    detail_url = reverse('comment-detail', kwargs={'title_id': title_id,
                                                   'review_id': review_id,
                                                   'pk': comment_id})
    data = {'text': 'Updated comment'}

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_clients_for_users()
        cls.not_auth_client = APIClient()
        super().setUpTestData()

    def setUp(self):
        data = {'text': 'Some comment text'}
        url = reverse('comment-list', kwargs={'title_id': self.title_id,
                                              'review_id': self.review_id})
        self.user_client.post(url, data=data)

    def test_update_comment_by_author(self):
        response = self.user_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], self.data['text'])

    def test_update_comment_by_moderator(self):
        response = self.moderator_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_by_admin(self):
        response = self.admin_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_by_user_not_author(self):
        client = create_client_for_user()
        response = client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_by_not_auth_user(self):
        response = self.not_auth_client.patch(self.detail_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_invalid_path(self):
        detail_url = reverse('comment-detail', kwargs={'title_id': self.title_id,
                                                       'review_id': self.review_id,
                                                       'pk': 35})
        response = self.admin_client.patch(detail_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment_invalid_data(self):
        data = {'text': ''}
        response = self.admin_client.patch(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_comment_by_not_auth_user(self):
        response = self.not_auth_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_by_author(self):
        response = self.user_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_by_moderator(self):
        response = self.moderator_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_by_admin(self):
        response = self.admin_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_by_user_not_author(self):
        client = create_client_for_user()
        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
