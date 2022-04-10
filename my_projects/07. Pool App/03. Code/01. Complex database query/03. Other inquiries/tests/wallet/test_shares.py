from django.urls import reverse_lazy
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from apps.auth_core.choices import UserType
from apps.auth_core.tests.factories.user import UserFanFactory
from apps.profile.tests.factories.user_shares import UserSharesFactory
from services.api.filters_classes import WalletSharesListFilter


class WalletSharesListTestsCase(APITestCase):
    faker = Faker()
    url = reverse_lazy('api:wallet_shares_list')

    def setUp(self):
        self.user = UserFanFactory()

    def test_available_unauthorized(self):
        """
        Checking that an unauthorized user cannot access this api
        """
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fan_only(self):
        """
        Only a fan has access to this api
        For other types the status should be 403
        """
        user_type_list = list(UserType)
        user_type_fan = user_type_list.pop(UserType.FAN.value)

        # Check fan access
        self.user.type = user_type_fan
        self.user.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check other types of access
        for user_type in user_type_list:
            self.user.type = user_type
            self.user.save()

            self.client.force_authenticate(user=self.user)
            response = self.client.get(self.url, format='json')

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_authorized_user_orders(self):
        """Api will only give out orders of an authorized user"""
        # Creating data
        UserSharesFactory(user=self.user)
        UserSharesFactory()
        expected_count_orders = 1

        # Request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), expected_count_orders)

    def test_search_artist_name(self):
        """Checking Artist Name Search"""
        # Creating data
        UserSharesFactory(user=self.user, artist__name='Name 1')
        search_artist = UserSharesFactory(
            user=self.user, artist__name='Name 2',
        )

        # Request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url, data={'search': search_artist.artist.name},
            format='json',
        )

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['artist_name'],
            search_artist.artist.name,
        )

    def test_filter_view_all(self):
        """
        The Api must accept the view_all filter
        If view_all == False then the first 6 entries will be output
        If view_all == True then the first 6 records will be excluded
        By default view_all == False
        """
        # Creating data
        count_orders = 20
        initial_order_quantity = WalletSharesListFilter.INITIAL_ORDER_QUANTITY
        for order in range(0, count_orders):
            UserSharesFactory(user=self.user)

        # Request view_all == false
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url, data={'view_all': False}, format='json',
        )

        # Check view_all == false
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), initial_order_quantity)

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], count_orders)

        # Request view_all == true
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url, data={'view_all': True}, format='json',
        )

        # Check view_all == true
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            len(response.data['results']),
            count_orders - initial_order_quantity,
        )

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], count_orders)

        # Request view_all not transferred
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')

        # Check view_all == true
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), initial_order_quantity)

        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], count_orders)

    def test_filter_view_all_few_records(self):
        """Checking the behavior of the api when there are few entries"""
        # Creating data
        count_orders = WalletSharesListFilter.INITIAL_ORDER_QUANTITY - 1
        for order in range(0, count_orders):
            UserSharesFactory(user=self.user)

        # Request view_all == false
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url, data={'view_all': False}, format='json',
        )

        # Check view_all == false
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), count_orders)

        # Request view_all == true
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.url, data={'view_all': True}, format='json',
        )

        # Check view_all == true
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 0)
