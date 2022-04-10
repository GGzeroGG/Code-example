from unittest import mock

from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Device


class LogoutTest(APITestCase):
    URL = reverse_lazy('api:user_logout')
    URL_AUTH = reverse_lazy('api:user_auth')

    @mock.patch('google.oauth2.id_token.verify_oauth2_token', return_value={
        'iss': 'https://accounts.google.com',
        'email': 'test@gmail.com',
        'given_name': 'name',
        'family_name': '',
    })
    def test_device_delete(self, fake_func):
        """
        Checking that the device is removed
        """
        # Imitation of authorization
        data_auth = {
            'google_token': 'good_token',
            'device': {
                'device_id': 'device_id',
                'registration_token': '2',
                'os_version': '2',
                'os_name': Device.OS.ANDROID,
            },
            'language': 'ru',
        }
        response_auth = self.client.post(
            self.URL_AUTH, data_auth, format='json'
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='JWT ' + response_auth.data['token']
        )

        response = self.client.post(self.URL, format='json')
        device = Device.objects.filter(device_id='device_id').last()

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(device)

