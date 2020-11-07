import datetime

from django.db import models
from django.utils import timezone
# from django.apps import apps
# Partner = apps.get_model('projects', 'Partner')
from django.contrib.auth.models import User
class Student(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_address = models.EmailField(primary_key=True) # NEED TO PRIMARY KEY
    full_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=200)
    college = models.CharField(max_length=200)
    major = models.CharField(max_length=200)
    year = models.CharField(max_length=100)
    first_choice = models.CharField(max_length=1000, default= None)
    second_choice = models.CharField(max_length=1000, default= None)
    third_choice = models.CharField(max_length=1000, default= None)
    # first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.email_address

class Answer(models.Model):
    # student = models.ForeignKey(Student, on_delete=models.CASCADE) # PRIMARY KEY
    email_address = models.EmailField(primary_key=True)
    question = models.ForeignKey('projects.Question', on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000)
    def __str__(self):
        return self.answer_text
