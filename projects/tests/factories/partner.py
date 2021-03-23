import factory

class PartnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'projects.Partner'
    email_address =factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
