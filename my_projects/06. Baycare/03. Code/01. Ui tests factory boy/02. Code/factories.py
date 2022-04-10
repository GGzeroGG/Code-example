import factory
from factory.django import DjangoModelFactory

from apps.distributors.tests.factories import DistributorFactory
from apps.farmers.choices import FarmingStyleChoices
from apps.offer.models import Offer, OfferComponent, \
    OfferDistributor, OfferFarmer, OfferComponentRecipient
from apps.products.choices.component import ComponentUnit
from apps.products.tests.factories import ProductFactory
from services.api.tests.farmers.factories import FarmerFactory


class OfferFactory(DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    farmer = factory.SubFactory(FarmerFactory)
    distributor = factory.SubFactory(DistributorFactory)

    hectares = 1
    seeds_per_m = 1
    notes = factory.Faker('name')

    class Meta:
        model = Offer


class OfferComponentFactory(DjangoModelFactory):
    offer = factory.SubFactory(OfferFactory)

    name = factory.Faker('name')
    price = 1
    count = 2
    tax = 2
    unit = ComponentUnit.SEEDS.value

    class Meta:
        model = OfferComponent


class OfferComponentRecipientFactory(DjangoModelFactory):
    offer_component = factory.SubFactory(OfferComponentFactory)

    company = factory.Faker('company')
    agents_name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    country = factory.Faker('current_country')
    city = factory.Faker('region')
    postcode = factory.Faker('postcode')

    class Meta:
        model = OfferComponentRecipient


class OfferDistributorFactory(DjangoModelFactory):
    offer = factory.SubFactory(OfferFactory)

    company = factory.Faker('company')
    agents_name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    country = factory.Faker('current_country')
    city = factory.Faker('region')
    postcode = factory.Faker('postcode')

    class Meta:
        model = OfferDistributor


class OfferFarmerFactory(DjangoModelFactory):
    offer = factory.SubFactory(OfferFactory)

    company = factory.Faker('company')
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    country = factory.Faker('current_country')
    city = factory.Faker('region')
    postcode = factory.Faker('postcode')
    farming_style = FarmingStyleChoices.ORGANIC.value

    class Meta:
        model = OfferFarmer
