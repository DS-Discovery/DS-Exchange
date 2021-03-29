import factory
from projects.tests.factories.project import ProjectFactory

class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'projects.Question'
    project = factory.SubFactory(ProjectFactory)
    question_text = factory.Faker('sentence')
    question_type = 'text'
