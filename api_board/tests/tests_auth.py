from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse


class TestAuth(TestCase):
    url = reverse('get-confirmation_code')

    def test_sending_email(self):
        self.client.post(self.url, data={"email": "testded@mail.ru"}, format='json')
        email = mail.outbox
        self.assertEqual(len(email), 1, msg="Email doesn't send after registration")
        self.assertIn('confirmation code', email[0].body, msg="Email body doesn't contains str:confirmation code")

    def test_generating_username_from_email(self):
        self.url = reverse('get-confirmation_code')
        response = self.client.post(self.url, data={"email": "testded@mail.ru"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('username'))

    def test_invalid_email(self):
        invalid_email = 'invalid'
        self.url = reverse('get-confirmation_code')
        response = self.client.post(self.url, data={"email": invalid_email}, format='json')
        self.assertContains(response, "Enter a valid email address.",
                            status_code=status.HTTP_400_BAD_REQUEST)

    def test_get_token(self):
        data = {"email": "testded@mail.ru"}
        self.client.post(self.url, data=data, format='json')

        email = mail.outbox[0]
        confirmation_code = email.body.split('confirmation code')
        data['confirmation_code'] = confirmation_code[-1].strip()
        url = reverse('get-token')
        response = self.client.post(url, data=data)
        self.assertIn('token', response.data)
        self.assertIsInstance(response.data['token'], str)

        # Confirmation code works one time
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
