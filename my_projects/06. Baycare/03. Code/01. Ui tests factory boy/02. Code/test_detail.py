from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from apps.offer.tests.factories import OfferFactory, OfferComponentFactory, \
    OfferDistributorFactory, OfferFarmerFactory, OfferComponentRecipientFactory
from apps.products.tests.factories import ServicesFactory
from apps.reports.tests.factories.report import ReportFactory
from services.api.tests.auth.factories import AgentFactory


class OfferDetailTestCase(APITestCase):
    faker = Faker('es_ES')
    COUNT_OFFER_COMPONENT = 2
    COUNT_PRODUCT_SERVICE = 2

    def setUp(self):
        self.offer = OfferFactory()
        offer_component_1 = OfferComponentFactory(offer=self.offer)
        offer_component_2 = OfferComponentFactory(offer=self.offer)
        OfferDistributorFactory(offer=self.offer)
        OfferFarmerFactory(offer=self.offer)
        self.recipient_1 = OfferComponentRecipientFactory(
            offer_component=offer_component_1,
        )
        self.recipient_2 = OfferComponentRecipientFactory(
            offer_component=offer_component_2,
        )
        ServicesFactory.create_batch(self.COUNT_PRODUCT_SERVICE,
                                     product=self.offer.product)

    def test_no_authenticate(self):
        """
        The user may not be authorized
        """
        url = reverse('api:offer_detail', kwargs={
            'token': self.offer.token,
        })
        response = self.client.get(url, format='json')

        # Check
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_data_check(self):
        """
        Checking the output
        """
        url = reverse('api:offer_detail', kwargs={
            'token': self.offer.token,
        })
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('offer_farmer', response.data)
        self.assertEqual(
            response.data['offer_farmer']['phone'],
            self.offer.offer_farmer.phone,
        )
        self.assertIn('offer_distributor', response.data)
        self.assertEqual(
            response.data['offer_distributor']['phone'],
            self.offer.offer_distributor.phone,
        )
        self.assertIn('offer_components', response.data)
        self.assertEqual(
            len(response.data['offer_components']), self.COUNT_OFFER_COMPONENT,
        )

        self.assertIn('product', response.data)
        self.assertIn('services', response.data['product'])
        self.assertEqual(
            len(response.data['product']['services']),
            self.COUNT_OFFER_COMPONENT,
        )
        self.assertNotIn('report_exists', response.data)

    def test_check_report_exists(self):
        """
        If the distributor is authorized, then the report_exists field should
        appear, which says whether a report has been left for this offer
        """
        self.client.force_authenticate(AgentFactory())
        ReportFactory(offer=self.offer)
        url = reverse('api:offer_detail', kwargs={
            'token': self.offer.token,
        })
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('offer_farmer', response.data)
        self.assertEqual(
            response.data['offer_farmer']['phone'],
            self.offer.offer_farmer.phone,
        )
        self.assertIn('offer_distributor', response.data)
        self.assertEqual(
            response.data['offer_distributor']['phone'],
            self.offer.offer_distributor.phone,
        )
        self.assertIn('offer_components', response.data)
        self.assertEqual(
            len(response.data['offer_components']), self.COUNT_OFFER_COMPONENT,
        )

        self.assertIn('product', response.data)
        self.assertIn('services', response.data['product'])
        self.assertEqual(
            len(response.data['product']['services']),
            self.COUNT_OFFER_COMPONENT,
        )
        self.assertIn('report_exists', response.data)
        self.assertEqual(response.data['report_exists'], True)

    def test_no_token(self):
        """
        Incorrectly transmitted token
        """
        url = reverse('api:offer_detail', kwargs={
            'token': '123',
        })
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
