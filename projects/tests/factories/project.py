import factory
from faker import Faker
import random

import json

from students.models import Student

fake = Faker()

def generate_skills(arg):
    skillset = {}
    for _ in range(1,random.randint(1, 9)):
         # skillset[random.choice(list(Student.default_skills))] = random.choice(list(filter(None, Student.skill_levels_options.values())))
        skillset[fake.word()] = fake.word()
    return skillset

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'projects.Project'
    project_name = factory.Faker('sentence')
    organization = factory.Faker('word')
    embed_link = factory.Faker('url')
    semester = 'SP21'
    project_category = factory.LazyAttribute(lambda o: ';'.join(fake.words(random.randint(1, 9))))
    student_num = factory.Faker('random_number')
    description = factory.Faker('paragraph')
    organization_description = factory.Faker('paragraph')
    timeline = factory.Faker('paragraph')
    project_workflow = factory.Faker('paragraph')
    dataset = factory.Faker('word')
    deliverable = factory.Faker('paragraph')
    skillset = factory.LazyAttribute(generate_skills)
    additional_skills = factory.Faker('paragraph')
    technical_requirements = factory.Faker('paragraph')
