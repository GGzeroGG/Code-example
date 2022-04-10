from unittest import mock

from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from apps.distributors.tests.factories import DistributorFactory
from apps.offer.models import Offer, OfferComponent, OfferDistributor, \
    OfferFarmer, OfferComponentRecipient
from apps.products.tests.factories import ProductFactory, ComponentFactory
from services.api.tests.auth.factories import AgentFactory
from services.api.tests.farmers.factories import FarmerFactory


class OfferTestCase(APITestCase):
    url = reverse_lazy('api:offer_create')
    faker = Faker('es_ES')

    def setUp(self):
        self.user = AgentFactory()
        DistributorFactory(agent=self.user)
        self.farmer = FarmerFactory()
        self.product = ProductFactory()
        self.component = ComponentFactory(product=self.product)

    @mock.patch('services.api.views.offer.distributor.create.send_email')
    def test_no_authenticate(self, mocked_send_email):
        """
        The user must be authorized
        """
        data = {
            'product': self.product.id,
            'farmer': self.farmer.id,
            'hectares': 1.1,
            'seeds_per_m': 1.2,
            'notes': self.faker.name(),
        }
        response = self.client.post(self.url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mocked_send_email.delay.assert_not_called()

    @mock.patch('services.api.views.offer.distributor.create.send_email')
    def test_create_offer(self, mocked_send_email):
        """
        Successful co-creation of an offer
        """
        self.client.force_authenticate(self.user)
        data = {
            'product': self.product.id,
            'farmer': self.farmer.id,
            'hectares': 1.1,
            'seeds_per_m': 1.2,
            'notes': self.faker.name(),
        }
        response = self.client.post(self.url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer = Offer.objects.filter(
            product_id=self.product.id,
            farmer_id=self.farmer.id,
            hectares=data['hectares'],
            seeds_per_m=data['seeds_per_m'],
            notes=data['notes'],
        ).first()
        self.assertIsNotNone(offer)
        self.assertTrue(
            OfferComponent.objects.filter(offer_id=offer.id).exists(),
        )
        self.assertTrue(
            OfferDistributor.objects.filter(offer_id=offer.id).exists(),
        )
        self.assertTrue(
            OfferFarmer.objects.filter(offer_id=offer.id).exists(),
        )

        offer_component = OfferComponent.objects.filter(
            offer_id=offer.id).first()
        self.assertTrue(
            OfferComponentRecipient.objects.filter(
                offer_component_id=offer_component.id,
            ).exists(),
        )
        mocked_send_email.delay.assert_called_once()
