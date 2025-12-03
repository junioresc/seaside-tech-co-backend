import factory

from apps.orgs.models import Organization, Store


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker("company")
    timezone = "America/Los_Angeles"
