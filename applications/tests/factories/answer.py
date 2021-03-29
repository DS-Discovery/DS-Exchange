import factory
from students.tests.factories.student import StudentFactory
from applications.tests.factories.application import ApplicationFactory
from projects.tests.factories.question import QuestionFactory

class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'applications.Answer'
    student = factory.SubFactory(StudentFactory)
    application = factory.SubFactory(ApplicationFactory)
    question = factory.SubFactory(QuestionFactory)
    answer_text = factory.Faker('paragraph')
