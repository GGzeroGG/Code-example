from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from apps.distributors.tests.factories import DistributorFactory
from apps.offer.choices.offer import OfferStatus
from apps.offer.models import Offer, OfferComponent, OfferComponentRecipient
from apps.offer.tests.factories import OfferFactory, OfferComponentFactory, \
    OfferComponentRecipientFactory
from services.api.tests.auth.factories import AgentFactory, AdminFactory


class ReportUpdateTestCase(APITestCase):
    faker = Faker('es_ES')

    def setUp(self):
        self.agent = AgentFactory()
        DistributorFactory(agent=self.agent)
        self.offer: Offer = OfferFactory(
            distributor=self.agent.distributor,
            status=OfferStatus.ACCEPTED.value,
        )
        self.offer_component: OfferComponent = OfferComponentFactory(
            offer=self.offer,
        )
        self.recipient: OfferComponentRecipient = \
            OfferComponentRecipientFactory(
                offer_component=self.offer_component
            )

        self.alien_recipient = OfferComponentRecipientFactory(
            offer_component__offer__status=OfferStatus.ACCEPTED.value,
        )

    def test_user_is_not_authorized(self):
        """
        The user must be authorized
        """
        url = reverse_lazy('api:recipient_update', kwargs={
            'pk': self.recipient.id,
        })
        data = {
            'company': self.faker.company(),
            'agents_name': self.faker.name(),
            'phone': self.faker.phone_number().replace(' ', ''),
            'email': self.faker.company_email(),
            'country': self.faker.current_country(),
            'city': self.faker.region(),
            'postcode': self.faker.postcode(),
        }

        response = self.client.patch(url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_distributor(self):
        """
        Api only for distributor if there is another role expects error 403
        """
        self.client.force_authenticate(AdminFactory())
        url = reverse_lazy('api:recipient_update', kwargs={
            'pk': self.recipient.id,
        })
        data = {
            'company': self.faker.company(),
            'agents_name': self.faker.name(),
            'phone': self.faker.phone_number().replace(' ', ''),
            'email': self.faker.company_email(),
            'country': self.faker.current_country(),
            'city': self.faker.region(),
            'postcode': self.faker.postcode(),
        }

        response = self.client.patch(url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recipient_update(self):
        """
        Successful recipient update
        """
        self.client.force_authenticate(self.agent)
        url = reverse_lazy('api:recipient_update', kwargs={
            'pk': self.recipient.id,
        })
        data = {
            'company': self.faker.company(),
            'agents_name': self.faker.name(),
            'phone': self.faker.phone_number().replace(' ', ''),
            'email': self.faker.company_email(),
            'country': self.faker.current_country(),
            'city': self.faker.region(),
            'postcode': self.faker.postcode(),
        }
        response = self.client.patch(url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipient.refresh_from_db()
        for field in data:
            self.assertEqual(getattr(self.recipient, field), data[field])

    def test_update_someone_else_offer(self):
        """
        If you try to update someone else's offer, there will be a 404 error
        """
        self.client.force_authenticate(self.agent)
        url = reverse_lazy('api:recipient_update', kwargs={
            'pk': self.alien_recipient.id,
        })
        data = {
            'company': self.faker.company(),
            'agents_name': self.faker.name(),
            'phone': self.faker.phone_number().replace(' ', ''),
            'email': self.faker.company_email(),
            'country': self.faker.current_country(),
            'city': self.faker.region(),
            'postcode': self.faker.postcode(),
        }
        response = self.client.patch(url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_only_offer_status_accepted(self):
        """
        You can only update the offers with the status of accepted, otherwise
         the error 404
        """
        self.offer.status = OfferStatus.CONFIRMED.value
        self.offer.save()

        self.client.force_authenticate(self.agent)
        url = reverse_lazy('api:recipient_update', kwargs={
            'pk': self.recipient.id,
        })
        data = {
            'company': self.faker.company(),
            'agents_name': self.faker.name(),
            'phone': self.faker.phone_number().replace(' ', ''),
            'email': self.faker.company_email(),
            'country': self.faker.current_country(),
            'city': self.faker.region(),
            'postcode': self.faker.postcode(),
        }
        response = self.client.patch(url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
