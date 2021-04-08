import factory

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'projects.Project'
    project_name = factory.Faker('sentence')
    organization = factory.Faker('word')
    embed_link = factory.Faker('url')
    semester = 'SP21'
    project_category = factory.LazyAttribute(lambda o: ';'.join(factory.Faker('words')))
    student_num = factory.Faker('random_number')
    description = factory.Faker('paragraph')
    organization_description = factory.Faker('paragraph')
    timeline = factory.Faker('paragraph')
    project_workflow = factory.Faker('paragraph')
    dataset = factory.Faker('word')
    deliverable = factory.Faker('paragraph')
    skillset = factory.Faker('json')
    additional_skills = factory.Faker('paragraph')
    technical_requirements = factory.Faker('paragraph')
