from pathlib import Path

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_board.models import Review, Title
from api_board.tests.common import (
    create_clients_for_users,
    get_user_from_client,
    create_client_for_user
)


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent/'fixtures', ])
class TestReview(TestCase):
    fixtures = ['reviews', 'titles', 'categories', 'users', 'genres']
    title_id = 1
    review_id = 1
    list_url = reverse('review-list', kwargs={'title_id': title_id})
    detail_url = reverse('review-detail', kwargs={'title_id': title_id,
                                                  'pk': review_id})
    data = {'text': 'Some text', 'score': 5}

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_clients_for_users()
        cls.not_auth_client = APIClient()
        super().setUpTestData()

    def test_review_list_pagination(self):
        response = self.user_client.get(self.list_url)
        self.assertEqual(response.data.get('count'), Review.objects.count())
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)

    def test_review_list_response_data(self):
        response = self.user_client.get(self.list_url)
        data = response.json()['results'][0]
        review = Review.objects.get(id=data['id'])
        self.check_response_data(data, review)

    def check_response_data(self, data, review):
        self.assertEqual(data['id'], review.id)
        self.assertEqual(data['author'], review.author.username)
        self.assertEqual(data['title'], review.title.name)
        self.assertEqual(data['text'], review.text)
        self.assertEqual(data['score'], review.score)

    def test_review_list_invalid_path(self):
        url = reverse('review-list', kwargs={'title_id': 35})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review(self):
        response = self.user_client.post(self.list_url, data=self.data)
        title = Title.objects.get(id=self.title_id)
        author = get_user_from_client(self.user_client)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], author.username)
        self.assertEqual(response.data['title'], title.name)
        self.assertEqual(response.data['score'], self.data['score'])
        self.assertEqual(response.data['text'], self.data['text'])
        review = Review.objects.get(id=response.data['id'])
        self.check_response_data(response.data, review)

    def test_create_review_twice_for_one_user(self):
        self.user_client.post(self.list_url, data=self.data)
        response = self.user_client.post(self.list_url, data={'text': 'Some other', 'score': 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_field_score_validators(self):
        response = self.user_client.post(self.list_url, data={'text': 'Some text', 'score': 11})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.user_client.post(self.list_url, data={'text': 'Some text', 'score': 0.8})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_path(self):
        url = reverse('review-list', kwargs={'title_id': 35})
        response = self.user_client.post(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review_for_not_aut_user(self):
        response = self.not_auth_client.post(self.list_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_review(self):
        response = self.user_client.get(self.detail_url)
        data = response.json()
        review = Review.objects.get(id=self.review_id)
        self.check_response_data(data, review)

    def test_get_review_invalid_path(self):
        url = reverse('review-detail', kwargs={'title_id': self.title_id,
                                               'pk': 35})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(FIXTURE_DIRS=[Path(__file__).resolve().parent / 'fixtures', ])
class TestReviewUpdateDelete(TestCase):
    fixtures = ['titles', 'categories', 'users', 'genres']
    title_id = 1
    review_id = 1
    detail_url = reverse('review-detail', kwargs={'title_id': title_id,
                                                  'pk': review_id})
    data = {'text': 'Updated review'}

    @classmethod
    def setUpTestData(cls):
        cls.user_client, cls.moderator_client, cls.admin_client = create_clients_for_users()
        cls.not_auth_client = APIClient()
        super().setUpTestData()

    def setUp(self):
        data = {'text': 'Some text', 'score': 5}
        url = reverse('review-list', kwargs={'title_id': self.title_id})
        self.user_client.post(url, data=data)

    def test_update_review_by_author(self):
        response = self.user_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], self.data['text'])

    def test_update_review_by_moderator(self):
        response = self.moderator_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_review_by_admin(self):
        response = self.admin_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_review_by_user_not_author(self):
        client = create_client_for_user()
        response = client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_invalid_data(self):
        data = {'text': ''}
        response = self.admin_client.patch(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_by_not_auth_user(self):
        response = self.not_auth_client.patch(self.detail_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_by_author(self):
        response = self.user_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_by_moderator(self):
        response = self.moderator_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_by_admin(self):
        response = self.admin_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_by_user_not_author(self):
        client = create_client_for_user()
        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_not_auth_user(self):
        response = self.not_auth_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
