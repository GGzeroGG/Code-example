from datetime import timedelta
from decimal import Decimal

from django.db.models import F
from django.urls import reverse_lazy
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from apps.artists.models import ChangeSharePrice
from apps.artists.tests.factories.artist import ArtistFactory
from apps.auth_core.choices import UserType
from apps.profile.tests.factories.profile import ProfileFactory
from apps.profile.tests.factories.user_shares import UserSharesFactory
from apps.profile.tests.factories.wallet import WalletFactory


class WalletSharesTestsCase(APITestCase):
    faker = Faker()
    url = reverse_lazy('api:wallet_shares')

    def setUp(self):
        self.wallet = WalletFactory()
        self.artist = ArtistFactory(price=10)
        self.artist_2 = ArtistFactory(price=5)
        ProfileFactory(user=self.wallet.user)

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
        self.wallet.user.type = user_type_fan
        self.wallet.user.save()

        self.client.force_authenticate(user=self.wallet.user)
        response = self.client.get(self.url, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check other types of access
        for user_type in user_type_list:
            self.wallet.user.type = user_type
            self.wallet.user.save()

            self.client.force_authenticate(user=self.wallet.user)
            response = self.client.get(self.url, format='json')

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data_for_day(self):
        """
        Checking the result for the day

        current_price_artist_1 = 20 = сpa1
        current_price_artist_2 = 5 = сpa2
        artist_1_price_day_ago = 10 = a1pda
        artist_2_price_day_ago = 10 = a2pda
        total_shares_worth = сpa1 + сpa2 = 25 = tsw
        total_share_price_day_ago = a1pda + a2pda = 20 = tspda
        price_difference = tsw - tspda = 5 = pd
        price_difference_percent = (tsw - tspda) / tspda * 100 = 25% = pdp
        """
        # Create data
        current_price_artist_1 = 20
        current_price_artist_2 = 5
        artist_1_price_day_ago = 10
        artist_2_price_day_ago = 10
        total_shares_worth = 25
        price_difference = 5
        price_difference_percent = 25

        self.artist.price = current_price_artist_1
        self.artist.save()

        self.artist_2.price = current_price_artist_2
        self.artist_2.save()

        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist,
        )
        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist_2,
        )

        change_price_day_artist = ChangeSharePrice.objects.create(
            artist=self.artist, changed_price=artist_1_price_day_ago,
        )
        change_price_day_artist.created_timestamp = \
            F('created_timestamp') - timedelta(hours=12)
        change_price_day_artist.save()

        change_price_day_artist_2 = ChangeSharePrice.objects.create(
            artist=self.artist_2, changed_price=artist_2_price_day_ago,
        )
        change_price_day_artist_2.created_timestamp = \
            F('created_timestamp') - timedelta(hours=12)
        change_price_day_artist_2.save()

        # Request
        self.client.force_authenticate(user=self.wallet.user)
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('total_shares_worth', response.data)
        self.assertEqual(
            response.data['total_shares_worth'],
            str(Decimal(total_shares_worth).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_day', response.data)
        self.assertEqual(
            response.data['difference_for_day'],
            str(Decimal(price_difference).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_day_percentage', response.data)
        self.assertEqual(
            response.data['difference_for_day_percentage'],
            str(Decimal(price_difference_percent).quantize(Decimal('1.00'))),
        )

    def test_response_data_for_week(self):
        """
        Checking the result for the week

        current_price_artist_1 = 5 = сpa1
        current_price_artist_2 = 5 = сpa2
        artist_1_price_week_ago = 10 = a1pwa
        artist_2_price_week_ago = 10 = a2pwa
        total_shares_worth = сpa1 + сpa2 = 10 = tsw
        total_share_price_week_ago = a1pwa + a2pwa = 20 = tspwa
        price_difference = tsw - tspda = -10 = pd
        price_difference_percent = (tsw - tspda) / tspda * 100 = -50% = pdp
        """
        # Create data
        current_price_artist_1 = 5
        current_price_artist_2 = 5
        artist_1_price_week_ago = 10
        artist_2_price_week_ago = 10
        total_shares_worth = 10
        price_difference = -10
        price_difference_percent = -50

        self.artist.price = current_price_artist_1
        self.artist.save()

        self.artist_2.price = current_price_artist_2
        self.artist_2.save()

        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist,
        )
        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist_2,
        )

        change_price_day_artist = ChangeSharePrice.objects.create(
            artist=self.artist, changed_price=artist_1_price_week_ago,
        )
        change_price_day_artist.created_timestamp = \
            F('created_timestamp') - timedelta(days=6)
        change_price_day_artist.save()

        change_price_day_artist_2 = ChangeSharePrice.objects.create(
            artist=self.artist_2, changed_price=artist_2_price_week_ago,
        )
        change_price_day_artist_2.created_timestamp = \
            F('created_timestamp') - timedelta(days=6)
        change_price_day_artist_2.save()

        # Request
        self.client.force_authenticate(user=self.wallet.user)
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('total_shares_worth', response.data)
        self.assertEqual(
            response.data['total_shares_worth'],
            str(Decimal(total_shares_worth).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_week', response.data)
        self.assertEqual(
            response.data['difference_for_week'],
            str(Decimal(price_difference).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_week_percentage', response.data)
        self.assertEqual(
            response.data['difference_for_week_percentage'],
            str(Decimal(price_difference_percent).quantize(Decimal('1.00'))),

        )

    def test_response_data_for_all(self):
        """
        Checking the result for the week

        current_price_artist_1 = 20 = сpa1
        current_price_artist_2 = 20 = сpa2
        purchase_price_artist_1 = 10 = ppa1
        purchase_price_artist_2 = 10 = ppa2
        total_shares_worth = сpa1 + сpa2 = 40 = tsw
        total_share_purchase_price = ppa1 + ppa2 = 20 = tspp
        price_difference = tsw - tspp = 20 = pd
        price_difference_percent = (tsw - tspp) / tspp * 100 = 100% = pdp
        """
        # Create data
        current_price_artist_1 = 20
        current_price_artist_2 = 20
        purchase_price_artist_1 = 10
        purchase_price_artist_2 = 10
        total_shares_worth = 40
        price_difference = 20
        price_difference_percent = 100

        self.artist.price = current_price_artist_1
        self.artist.save()

        self.artist_2.price = current_price_artist_2
        self.artist_2.save()

        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist,
            price=purchase_price_artist_1,
        )
        UserSharesFactory(
            user=self.wallet.user, count=1, artist=self.artist_2,
            price=purchase_price_artist_2,
        )

        # Request
        self.client.force_authenticate(user=self.wallet.user)
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('total_shares_worth', response.data)
        self.assertEqual(
            response.data['total_shares_worth'],
            str(Decimal(total_shares_worth).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_all', response.data)
        self.assertEqual(
            response.data['difference_for_all'],
            str(Decimal(price_difference).quantize(Decimal('1.00'))),
        )

        self.assertIn('difference_for_all_percentage', response.data)
        self.assertEqual(
            response.data['difference_for_all_percentage'],
            str(Decimal(price_difference_percent).quantize(Decimal('1.00'))),
        )
