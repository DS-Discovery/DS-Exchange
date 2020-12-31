import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Project(models.Model):

    project_name = models.CharField(max_length=200)
    organization = models.CharField(max_length=100)
    semester = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    project_category = models.CharField(max_length=100)
    student_num = models.IntegerField(default=0)
    description = models.CharField(max_length=5000)
    def __str__(self):
        return self.project_name


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
    question_num = models.IntegerField(default=0)
    question_text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=50, choices=question_choices, default='text')
    question_data =  models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.project.project_name + " - " + self.question_text