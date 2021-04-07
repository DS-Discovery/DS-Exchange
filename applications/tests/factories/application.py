import factory
from students.tests.factories.student import StudentFactory
from projects.tests.factories.project import ProjectFactory

class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'applications.Application'
    student = factory.SubFactory(StudentFactory)
    project = factory.SubFactory(ProjectFactory)
    status = "SUB"
