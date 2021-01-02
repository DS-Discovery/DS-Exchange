import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Semester(models.TextChoices):
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

    project_name = models.CharField(max_length=200)
    organization = models.CharField(max_length=100)
    # semester = models.CharField(max_length=100)
    # year = models.CharField(max_length=100)
    semester = models.CharField(max_length=4, choices=Semester.choices)
    project_category = models.CharField(max_length=100)
    student_num = models.IntegerField(default=0)
    description = models.CharField(max_length=5000)
    
    def __str__(self):
        return self.project_name

    def to_dict(self):
        return {
            "project_name": self.project_name,
            "organization": self.organization,
            "semester": self.sem_mapping[self.semester],
            "project_category": self.project_category.split(";"),
            "student_num": self.student_num,
            "description": self.description,
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

    def __str__(self):
        return self.project.project_name + " - " + self.question_text
