import factory
from students.models import Student
from projects.models import Semester
import random

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'students.Student'
    email_address = factory.Faker('email')
    student_id = factory.Faker('ssn')
    college = random.choice(Student.College.choices)[0]
    major = factory.Faker('word')
    year = random.choice(Semester.choices)[0]
    _skills = factory.Faker('json')
