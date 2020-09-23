import datetime

from django.db import models
from django.utils import timezone
# from django.apps import apps
# Partner = apps.get_model('projects', 'Partner')

class Student(models.Model):
    email_address = models.EmailField(primary_key=True) # NEED TO PRIMARY KEY
    full_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=200)
    college = models.CharField(max_length=200)
    major = models.CharField(max_length=200)
    year = models.CharField(max_length=100)
    first_choice = models.CharField(max_length=1000)
    second_choice = models.CharField(max_length=1000)
    third_choice = models.CharField(max_length=1000)

    def __str__(self):
        return self.full_name


class Question(models.Model):
    partner = models.ForeignKey('projects.Partner', on_delete=models.CASCADE, default="404")
    question_text = models.CharField(max_length=200)
    def create_id(partner, question_text):
        return hash(str(partner) + str(question_text))


    id = models.CharField(primary_key=True, default = create_id(partner, question_text), max_length = 200)

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default="404") # PRIMARY KEY
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000)
    def __str__(self):
        return self.answer_text
