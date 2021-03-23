import factory
from projects.tests.factories.partner import PartnerFactory
from projects.tests.factories.project import ProjectFactory

class PartnerProjectInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'projects.PartnerProjectInfo'
    role = factory.Faker('word')
    partner = PartnerFactory()
    project = ProjectFactory()
