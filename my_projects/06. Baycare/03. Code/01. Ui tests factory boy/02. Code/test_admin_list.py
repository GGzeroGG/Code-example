from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from apps.farmers.choices import FarmingStyleChoices
from apps.offer.choices.offer import OfferStatus
from apps.offer.models import Offer
from apps.offer.tests.factories import OfferFactory
from services.api.tests.auth.factories import AdminFactory


class OfferAdminListTestCase(APITestCase):
    url = reverse_lazy('api:offer_admin_list')
    COUNT_OFFERS_DISTRIBUTOR = 3

    def setUp(self):
        self.offer_accepted: Offer = OfferFactory(
            status=OfferStatus.CONFIRMED.value,
            hectares=10,
            farmer__farming_style=FarmingStyleChoices.CONVENTIONAL.value,
        )
        self.offer_accepted_2: Offer = OfferFactory(
            status=OfferStatus.CONFIRMED.value,
            hectares=20,
            farmer__farming_style=FarmingStyleChoices.ORGANIC.value,
        )
        self.admin = AdminFactory()

        self.offer_pending: Offer = OfferFactory(
            status=OfferStatus.PENDING.value,
            farmer__farming_style=FarmingStyleChoices.ORGANIC.value,
        )

    def test_no_authenticate(self):
        """
        The user must be authorized
        """
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_getting_offers(self):
        """
        Check that the distributor will only get their offers
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.COUNT_OFFERS_DISTRIBUTOR)

    def test_order_by_created_timestamp_increasing(self):
        """
        Check the sorting by date of creation in ascending order
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'ordering': 'created_timestamp',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['id'], self.offer_accepted.id,
        )

    def test_order_by_created_timestamp_decrease(self):
        """
        Check sorting by date of creation in descending order
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'ordering': '-created_timestamp',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['id'], self.offer_pending.id,
        )

    def test_filter_hectares(self):
        """
        Filter check by hectare
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'hectares__range': f'{self.offer_accepted.hectares - 1},'
                               f'{self.offer_accepted_2.hectares - 1}'
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'], self.offer_accepted.id,
        )

    def test_filter_status(self):
        """
        Filter check by status
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'status__in': OfferStatus.PENDING.value,
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'], self.offer_pending.id,
        )

    def test_filter_distributor(self):
        """
        Filter check by distributor
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'distributor_id__in': f'{self.offer_accepted.distributor_id},'
                                  f'{self.offer_accepted_2.distributor_id}',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_product(self):
        """
        Filter check by product
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'product_id__in': self.offer_accepted.product.id,
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'], self.offer_accepted.id,
        )

    def test_filter_farmer_style(self):
        """
        Filter check by farmer_style
        """
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url, data={
            'farming_style__in':
                self.offer_accepted.farmer.farming_style,
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'], self.offer_accepted.id,
        )
