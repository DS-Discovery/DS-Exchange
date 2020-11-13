import datetime

from django.db import models
from django.utils import timezone

class Project(models.Model):
    organization = models.CharField(max_length=100)

    project_name = models.CharField(max_length=200, primary_key=True)

    project_category = models.CharField(max_length=100)
    student_num = models.IntegerField(default=0)
    description = models.CharField(max_length=5000)
    def __str__(self):
        return self.project_name

class Partner(models.Model):
    email_address = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    projects = models.ManyToManyField(Project)


    def __str__(self):
        return self.email_address


class Question(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    # def create_id(partner, question_text):
    #     return hash(str(partner) + str(question_text))
    #
    #
    # id = models.CharField(primary_key=True, default = create_id(partner, question_text), max_length = 200)

    def __str__(self):
        return self.question_text
