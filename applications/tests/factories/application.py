import factory
from students.models.tests.factories.student import StudentFactory
from projects.tests.factories.project import ProjectFactory


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'applications.Application'
    student = StudentFactory()
    project = ProjectFactory()
