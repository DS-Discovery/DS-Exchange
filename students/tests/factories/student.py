import factory
from students.models import Student
from projects.models import Semester
from faker import Faker
import random

def generate_skills():
    skillset = {}
    for _ in range(1, random.randint(1, 9)):
         skillset[random.choice(list(Student.default_skills))] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
    return skillset


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'students.Student'
    email_address = factory.Faker('email')
    student_id = factory.Faker('ssn')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    college = random.choice(Student.College.choices)[0]
    major = factory.Faker('sentence')
    year = random.choice(Semester.choices)[0]
    resume_link = factory.Faker('url')

    general_question = factory.Faker('paragraph')
    additional_skills = factory.Faker('paragraph')
    _skills = factory.LazyFunction(lambda: generate_skills())
