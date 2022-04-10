from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from faker import Faker
from freezegun import freeze_time
from rest_framework.test import APITestCase

from apps.artists.models import ChangeSharePrice
from apps.artists.tests.factories.artist import ArtistFactory
from apps.profile.tests.factories.profile import ProfileFactory
from services.api.views.artists.get_price_change_graph import (
    GetPriceChangeGraphView,
)


class ArtistChangePriceGraphTestCase(APITestCase):
    faker = Faker()
    tz = timezone.get_current_timezone()

    def setUp(self):
        self.profile = ProfileFactory(avatar=None)
        self.artist = ArtistFactory(validated=True)

        self.view = GetPriceChangeGraphView()

    @freeze_time(datetime(2022, 1, 20, 11, 0, tzinfo=tz))
    def test_get_month_data(self):
        # rows grouped by weeks in calendar
        initial_data = [
            (Decimal('20.10'), datetime(2021, 12, 25, 10, tzinfo=self.tz)),
            (Decimal('32.10'), datetime(2021, 12, 25, 15, tzinfo=self.tz)),

            (Decimal('20.10'), datetime(2021, 12, 31, 12, tzinfo=self.tz)),
            (Decimal('30.20'), datetime(2022, 1, 1, 15, tzinfo=self.tz)),
            (Decimal('10.40'), datetime(2022, 1, 1, 12, tzinfo=self.tz)),
            (Decimal('35.00'), datetime(2022, 1, 2, 12, tzinfo=self.tz)),

            (Decimal('30.00'), datetime(2022, 1, 10, 15, tzinfo=self.tz)),
        ]
        for price, created_time in initial_data:
            record = ChangeSharePrice.objects.create(artist=self.artist,
                                                     changed_price=price)
            record.created_timestamp = created_time
            record.save(update_fields=['created_timestamp'])

        expected_data = [
            {'changed_price': Decimal('26.100'),
             'created_timestamp': datetime(2021, 12, 20, tzinfo=self.tz)},
            {'changed_price': Decimal('23.925'),
             'created_timestamp': datetime(2021, 12, 27, tzinfo=self.tz)},
            {'changed_price': Decimal('30.00'),
             'created_timestamp': datetime(2022, 1, 10, tzinfo=self.tz)}
        ]

        results = self.view._get_month_range_data(
            self.artist.change_share_prices.all(),
        )

        self.assertEqual(len(results), len(expected_data))

        for result, expected_result in zip(results, expected_data):
            self.assertEqual(
                result['changed_price'], expected_result['changed_price'],
            )
            self.assertEqual(
                result['created_timestamp'],
                expected_result['created_timestamp'],
            )

    @freeze_time(datetime(2021, 11, 2, 11, 0, tzinfo=tz))
    def test_get_day_data(self):
        initial_data = [
            (Decimal('20.50'), datetime(2021, 11, 1, 23, 40, tzinfo=self.tz)),
            (Decimal('30.50'), datetime(2021, 11, 1, 23, 50, tzinfo=self.tz)),

            (Decimal('20.10'), datetime(2021, 11, 2, 0, 10, tzinfo=self.tz)),
            (Decimal('30.20'), datetime(2021, 11, 2, 0, 20, tzinfo=self.tz)),
        ]
        for price, created_time in initial_data:
            record = ChangeSharePrice.objects.create(artist=self.artist,
                                                     changed_price=price)
            record.created_timestamp = created_time
            record.save(update_fields=['created_timestamp'])

        expected_data = [
            {'changed_price': Decimal('25.500'),
             'created_timestamp': datetime(2021, 11, 1, 23, tzinfo=self.tz)},
            {'changed_price': Decimal('25.150'),
             'created_timestamp': datetime(2021, 11, 2, tzinfo=self.tz)}
        ]

        results = self.view._get_day_range_data(
            self.artist.change_share_prices.all(),
        )

        self.assertEqual(
            results[0]['changed_price'], expected_data[0]['changed_price'],
        )
        self.assertEqual(
            results[0]['created_timestamp'],
            expected_data[0]['created_timestamp'],
        )

        self.assertEqual(
            results[1]['changed_price'], expected_data[1]['changed_price'],
        )
        self.assertEqual(
            results[1]['created_timestamp'],
            expected_data[1]['created_timestamp'],
        )

    @freeze_time(datetime(2021, 11, 2, 11, 0, tzinfo=tz))
    def test_get_week_data(self):
        initial_data = [
            (Decimal('20.50'), datetime(2021, 10, 30, 1, tzinfo=self.tz)),
            (Decimal('30.50'), datetime(2021, 10, 30, 2, tzinfo=self.tz)),

            (Decimal('20.10'), datetime(2021, 11, 1, 1, tzinfo=self.tz)),
            (Decimal('30.20'), datetime(2021, 11, 1, 2, tzinfo=self.tz)),
        ]
        for price, created_time in initial_data:
            record = ChangeSharePrice.objects.create(artist=self.artist,
                                                     changed_price=price)
            record.created_timestamp = created_time
            record.save(update_fields=['created_timestamp'])

        expected_data = [
            {'changed_price': Decimal('25.500'),
             'created_timestamp': datetime(2021, 10, 30, tzinfo=self.tz)},
            {'changed_price': Decimal('25.150'),
             'created_timestamp': datetime(2021, 11, 1, tzinfo=self.tz)}
        ]

        results = self.view._get_week_range_data(
            self.artist.change_share_prices.all(),
        )

        self.assertEqual(
            results[0]['changed_price'], expected_data[0]['changed_price'],
        )
        self.assertEqual(
            results[0]['created_timestamp'],
            expected_data[0]['created_timestamp'],
        )

        self.assertEqual(
            results[1]['changed_price'], expected_data[1]['changed_price'],
        )
        self.assertEqual(
            results[1]['created_timestamp'],
            expected_data[1]['created_timestamp'],
        )
