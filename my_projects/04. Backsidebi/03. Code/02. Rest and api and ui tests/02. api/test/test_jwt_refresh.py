from unittest import mock

from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Device


class LogoutTest(APITestCase):
    URL_REFRESH = reverse_lazy('api:jwt_refresh')
    URL_AUTH = reverse_lazy('api:user_auth')

    @mock.patch('google.oauth2.id_token.verify_oauth2_token', return_value={
        'iss': 'https://accounts.google.com',
        'email': 'test@gmail.com',
        'given_name': 'name',
        'family_name': '',
    })
    def test_jwt_refresh(self, fake_func):
        """
        Checking that the token is being updated
        """
        # Request authorization
        data = {
            'google_token': 'good_token',
            'device': {
                'device_id': 'device_id',
                'registration_token': '2',
                'os_version': '2',
                'os_name': Device.OS.ANDROID,
            },
            'language': 'ru',
        }
        response = self.client.post(self.URL_AUTH, data=data, format='json')

        # Check authorization
        jwt_token = response.data['token']
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Device.objects.filter(auth_token=jwt_token).exists())

        # Request refresh token
        data = {'token': jwt_token}
        response = self.client.post(self.URL_REFRESH, data=data, format='json')

        # Check refresh token
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Device.objects.filter(auth_token=jwt_token).exists())
