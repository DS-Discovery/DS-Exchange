import factory

class DataScholarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'students.DataScholar'
    email_address = factory.Faker('email')
