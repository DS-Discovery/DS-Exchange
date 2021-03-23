import factory
from students.models.tests.factories.student import StudentFactory
from applications.models.tests.factories.application import ApplicationFactory
from projects.models.tests.factories.question import QuestionFactory

class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'students.Answer'
    student = StudentFactory()
    application = ApplicationFactory()
    question = QuestionFactory()
    answer_text = factory.Faker('paragraph')
