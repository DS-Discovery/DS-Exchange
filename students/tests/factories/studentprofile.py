import factory
from students.models import Student
from projects.models import Semester, Project
import random

class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'students.Student'
    first_name = factory.Faker('word')
    last_name = factory.Faker('word')
    #email_address = factory.Faker('email')
    student_id = factory.Faker('ssn')
    college = random.choice(Student.College.choices)[0]
    major = factory.Faker('word')
    year = random.choice(Semester.choices)[0]
    general_question = factory.Faker('paragraph')
    additional_skills = factory.Faker('paragraph')
    # skillset = {}
    # for skill in Student.default_skills:
    #     skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.values())))
