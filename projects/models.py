import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_default_skills():
    return {
        "Python": "",
        "R": "",
        "SQL": "",
        "Tableau/Looker": "",
        "Data Visualization": "",
        "Data Manipulation": "",
        "Text Analysis": "",
        "Machine Learning/Deep Learning": "",
        "Geospatial Data, Tools and Libraries": "",
        "Web Development (frontend, backend, full stack)": "",
        "Mobile App Development": "",
        "Cloud Computing": "",
        "communication": "",
        "self-motivation": "",
        "leadership": "",
        "responsibility": "",
        "teamwork": "",
        "problem solving": "",
        "decisiveness": "",
        "good time management": "",
        "flexibility": ""
    }


class Semester(models.TextChoices):
    FA20 = ("FA20", _("Fall 2020"))
    SP21 = ("SP21", _("Spring 2021"))
    FA21 = ("FA21", _("Fall 2021"))
    SP22 = ("SP22", _("Spring 2022"))
    FA22 = ("FA22", _("Fall 2022"))
    SP23 = ("SP23", _("Spring 2023"))
    FA23 = ("FA23", _("Fall 2023"))
    SP24 = ("SP24", _("Spring 2024"))
    FA24 = ("FA24", _("Fall 2024"))
    SP25 = ("SP25", _("Spring 2025"))


class Project(models.Model):

    sem_mapping = {k: v for k, v in Semester.choices}
    email = models.EmailField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    organization = models.CharField(max_length=100, blank=True)
    organization_description = models.TextField(max_length=2000, blank=True)
    organization_website = models.URLField(blank=True)
    description = models.TextField(max_length=5000)
    timeline = models.CharField(max_length=1500, blank=True)
    other_project_category = models.CharField(max_length=100,  blank=True, null=True)
    project_workflow = models.CharField(max_length=1000, blank=True)
    dataset_availability = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=True)
    optional_q1 = models.CharField(max_length=200, blank=True, null=True)
    optional_q2 = models.CharField(max_length=200, blank=True, null=True)
    optional_q3 = models.CharField(max_length=200, blank=True, null=True)
    num_students = models.CharField(max_length=1, choices=
    (
        ('a', '3'),
        ('b', '4'),
        ('c', '5'),
        ('d', 'Other')
    ), default='a')
    other_num_students = models.IntegerField(blank=True, null=True)
    cloud_creds = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=True)
    meet_regularly = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=True)
    survey_response = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=True)
    hce_intern = models.CharField(max_length=1, choices=
    (
        ('a', 'Yes'),
        ('b', 'No'),
        ('c', 'Maybe')
    ), blank=True)
    environment = models.BooleanField(choices=((True, 'Yes'), (False, 'No')), default=True)
    marketing_channel = models.CharField(max_length=1, choices=
    (
        ('a', 'We reached out to you!'),
        ('b', 'Through a reference'),
        ('c', 'Social media'),
        ('d', 'Our website'),
        ('e', 'Prior participation'),
        ('f', 'Other')
    ), blank=True)
    other_marketing_channel = models.CharField(max_length=100,  blank=True, null=True)
    # semester = models.CharField(max_length=100)
    # year = models.CharField(max_length=100)
    embed_link = models.CharField(max_length=400, blank = True, null=True,)
    semester = models.CharField(max_length=4, choices=Semester.choices)
    project_category = models.CharField(max_length=200, blank=True, null=True)
    project_name = models.CharField(max_length=200)
    student_num = models.IntegerField(default=0)
    project_workflow = models.CharField(max_length=1000, blank=True)
    dataset = models.CharField(max_length=50, blank=True)
    deliverable = models.CharField(max_length=1000, blank=True)
    skillset = models.JSONField(default=get_default_skills, null=False)
    additional_skills = models.CharField(max_length=500, blank=True, null=True)
    technical_requirements = models.CharField(max_length=500, blank=True, null=True)
    # models.CharField(max_length=500, blank=True) # TODO: convert to JSON ala Student
    # TODO: dropdown for skills in admin view

    @property
    def num_applications(self):
        return Application.objects.filter(project=self).count()

    def __str__(self):
        return self.project_name

    def to_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            "id": self.id,
            "project_name": self.project_name,
            "organization": self.organization,
            "embed_link": self.embed_link,
            "semester": self.sem_mapping[self.semester],
            "project_category": self.project_category.split(";") if self.project_category != '' and self.project_category != None else [],
            "student_num": self.student_num,
            "description": self.description,
            "questions": [q.to_dict() for q in Question.objects.filter(project=self)],
            "timeline": self.timeline,
            "project_workflow": self.project_workflow,
            "dataset": self.dataset,
            "deliverable": self.deliverable,
            "skillset": self.skillset,
            "additional_skills": self.additional_skills,
            "technical_requirements": self.technical_requirements,
        }


class Partner(models.Model):
    email_address = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    projects = models.ManyToManyField(Project)

    def __str__(self):
        return self.email_address


class PartnerProjectInfo(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    def to_dict(self):
        return {
            "email_address": self.partner.email_address,
            "first_name": self.partner.first_name,
            "last_name": self.partner.last_name,
            "project": self.project.id,
        }


    def __str__(self):
        return f"{self.partner}+{self.project}"


class Question(models.Model):
    question_choices = (
        ('text','text'),
        ('mc','multiple choice'),
        ('dropdown', 'dropdown'),
        ('checkbox','checkbox'),
        ('multiselect','multiselect'),
        ('range','range'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # question_num = models.IntegerField(default=0)
    question_text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=50, choices=question_choices, default='text')
    question_data =  models.CharField(max_length=1000, null=True, blank=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project": self.project.id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "question_data": self.question_data,
        }

    def __str__(self):
        return self.project.project_name + " - " + self.question_text


from applications.models import Application
from students.models import Student