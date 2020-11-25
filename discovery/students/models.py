import datetime

from django.db import models
from django.utils import timezone
# from django.apps import apps
# Partner = apps.get_model('projects', 'Partner')
from django.contrib.auth.models import User
class Student(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    email_address = models.EmailField(max_length=100, primary_key= True) # NEED TO PRIMARY KEY
    first_name = models.CharField(max_length=100, null = True)
    last_name = models.CharField(max_length=100, null = True)
    # full_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=200)
    college = models.CharField(max_length=200)
    major = models.CharField(max_length=200)
    year = models.CharField(max_length=100)
    first_choice = models.CharField(max_length=1000, null=True, blank=True)
    second_choice = models.CharField(max_length=1000, null=True, blank=True)
    third_choice = models.CharField(max_length=1000, null=True, blank=True)

    resume_link = models.CharField(max_length=200, null = True, blank=True)
    general_question = models.CharField(max_length=1000, null = True, blank=True)

    def __str__(self):
        return self.email_address

class Answer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE) # PRIMARY KEY
    question = models.ForeignKey('projects.project', on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000)
    def __str__(self):
        return self.answer_text
