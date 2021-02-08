from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from api_board.models import Genre


class TestAuth(TestCase):

    def test_sending_email(self):
        client = APIClient()
        url = reverse('get-confirmation_code')
        client.post(url, data={"email": "testded@mail.ru"}, format='json')
        email = mail.outbox
        self.assertEqual(len(email), 1, msg="Email doesn't send after registration")
        self.assertIn('confirmation code', email[0].body, msg="Email body doesn't contains str:confirmation code")

    def test_generating_username_from_email(self):
        client = APIClient()
        url = reverse('get-confirmation_code')
        response = client.post(url, data={"email": "testded@mail.ru"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('username'))

    def test_invalid_email(self):
        invalid_email = 'invalid'
        client = APIClient()
        url = reverse('get-confirmation_code')
        response = client.post(url, data={"email": invalid_email}, format='json')
        self.assertContains(response, "Enter a valid email address.",
                            status_code=status.HTTP_400_BAD_REQUEST)


