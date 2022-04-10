from decimal import Decimal

from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.artists.tests.factories.artist import ArtistFactory
from apps.auth_core.choices import UserType
from apps.profile.tests.factories.user_shares import UserSharesFactory
from apps.profile.tests.factories.wallet import WalletFactory
from services.api.views.wallet.share import DetailShareView


class DetailShareTestsCase(APITestCase):
    faker = Faker()

    def setUp(self):
        self.wallet = WalletFactory()
        self.artist = ArtistFactory()

    def test_available_unauthorized(self):
        """
        Checking that an unauthorized user cannot access this api
        """
        url = reverse('api:wallet_detail_share', kwargs={
            'artist_id': self.artist.id,
        })
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fan_only(self):
        """
        Only a fan has access to this api
        For other types the status should be 403
        """
        url = reverse('api:wallet_detail_share', kwargs={
            'artist_id': self.artist.id,
        })
        user_type_list = list(UserType)
        user_type_fan = user_type_list.pop(UserType.FAN.value)

        # Check fan access
        self.wallet.user.type = user_type_fan
        self.wallet.user.save()

        self.client.force_authenticate(user=self.wallet.user)
        response = self.client.get(url, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check other types of access
        for user_type in user_type_list:
            self.wallet.user.type = user_type
            self.wallet.user.save()

            self.client.force_authenticate(user=self.wallet.user)
            response = self.client.get(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_exists_artist_or_shares(self):
        """Wrong artist_id or user has no shares"""
        # Request not exist shares
        self.client.force_authenticate(user=self.wallet.user)
        url = reverse('api:wallet_detail_share', kwargs={
            'artist_id': self.artist.id,
        })
        response = self.client.get(url, format='json')

        # Checks not exist shares
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIn('detail', response.data)
        self.assertEqual(
            response.data['detail'],
            DetailShareView.error_messages['not_shares'],
        )

        # Create data not exist artist
        UserSharesFactory(artist=self.artist, user=self.wallet.user)

        # Request not exist artist
        self.client.force_authenticate(user=self.wallet.user)
        url = reverse('api:wallet_detail_share', kwargs={'artist_id': 1000})
        response = self.client.get(url, format='json')

        # Checks not exist artist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIn('detail', response.data)
        self.assertEqual(
            response.data['detail'],
            DetailShareView.error_messages['not_shares'],
        )

    def test_successful_request(self):
        """The user has shares and the artist is found"""
        # Create data
        UserSharesFactory(artist=self.artist, user=self.wallet.user)

        # Request not exist artist
        self.client.force_authenticate(user=self.wallet.user)
        url = reverse('api:wallet_detail_share', kwargs={
            'artist_id': self.artist.id,
        })
        response = self.client.get(url, format='json')

        # Checks not exist artist
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_calculating_the_change_in_stock_prices(self):
        """
        Checking the correct calculation of this
        Raw data:
            Bought 5 shares at a price of $10 (share purchase 1 = sp1)
            Bought 20 shares at $40 (share purchase 2 = sp2)
            Current price $25 per share
        Calculations:
            Price changes for sp1
                Purchase amount = 5 * 10 = 50$
                Current price = 5 * 25 = 125$
                Price change = 125 - 50 = 75$
                Price change in % = (125 - 50) : 50 * 100 = 150%
            Price changes for sp2
                Purchase amount = 20 * 40 = 800$
                Current price = 20 * 25 = 500$
                Price change = 800 - 500 = -300$
                Price change in % = (500 - 800) : 800 * 100 = -37,5%
            Total price change sp1 and sp2
                Purchase price of all shares = 50 + 800 = 850$
                Current price of all shares = 125 + 500 = 625$
                Price change = 625 - 850 = -225$
                Price change in % = (625 - 850) : 850 * 100 ≈ -26,48%
        """
        # Create data
        share_purchase_1 = UserSharesFactory(
            count=5, price=10, user=self.wallet.user, artist=self.artist,
        )
        share_purchase_2 = UserSharesFactory(
            count=20, price=40, user=self.wallet.user, artist=self.artist,
        )

        self.artist.price = 25
        self.artist.save()

        # Create expected data
        price_change_sp1 = '75.00'
        price_change_in_interest_sp1 = '150.00'

        price_change_sp2 = '-300.00'
        price_change_in_interest_sp2 = '-37.50'

        current_price_sp1_and_sp2 = '625.00'
        price_change_in_interest_sp1_and_sp2 = '-26.48'

        # Request
        self.client.force_authenticate(user=self.wallet.user)
        url = reverse('api:wallet_detail_share', kwargs={
            'artist_id': self.artist.id,
        })
        response = self.client.get(url, format='json')

        # Checks data
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('shopping_list', response.data)

        response_share_purchase_1 = response.data['shopping_list'][1]
        self.assertIn('count', response_share_purchase_1)
        self.assertEqual(
            response_share_purchase_1['count'], share_purchase_1.count,
        )
        self.assertIn('difference_sum_price', response_share_purchase_1)
        self.assertEqual(
            response_share_purchase_1['difference_sum_price'],
            price_change_sp1,
        )
        self.assertIn(
            'difference_sum_price_percentage', response_share_purchase_1,
        )
        self.assertEqual(
            response_share_purchase_1['difference_sum_price_percentage'],
            price_change_in_interest_sp1,
        )

        response_share_purchase_2 = response.data['shopping_list'][0]
        self.assertIn('count', response_share_purchase_2)
        self.assertEqual(
            response_share_purchase_2['count'], share_purchase_2.count,
        )
        self.assertIn('difference_sum_price', response_share_purchase_2)
        self.assertEqual(
            response_share_purchase_2['difference_sum_price'],
            price_change_sp2,
        )
        self.assertIn(
            'difference_sum_price_percentage', response_share_purchase_2,
        )
        self.assertEqual(
            response_share_purchase_2['difference_sum_price_percentage'],
            price_change_in_interest_sp2,
        )

        self.assertIn('pooled_data', response.data)

        response_share_purchase_all = response.data['pooled_data']
        self.assertIn('total_count', response_share_purchase_all)
        self.assertEqual(
            response_share_purchase_all['total_count'],
            share_purchase_1.count + share_purchase_2.count,
        )
        self.assertIn('total_sum_current_price', response_share_purchase_all)
        self.assertEqual(
            response_share_purchase_all['total_sum_current_price'],
            current_price_sp1_and_sp2,
        )
        self.assertIn(
            'difference_total_sum_price_percentage',
            response_share_purchase_all,
        )
        self.assertEqual(
            response_share_purchase_all[
                'difference_total_sum_price_percentage'
            ],
            price_change_in_interest_sp1_and_sp2,
        )
