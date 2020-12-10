import datetime

from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    # def create_id(partner, question_text):
    #     return hash(str(partner) + str(question_text))
    #
    #
    # id = models.CharField(primary_key=True, default = create_id(partner, question_text), max_length = 200)

    def __str__(self):
        return self.project.project_name + " - " + self.question_text

@receiver(post_save, sender=Project)
def init_new_project(instance, created, raw, **kwargs):
    if created and not raw:

        skills = ["Python", "R", "SQL", "Tableau/Looker", "Data Visualization", 
                    "Data Manipulation", "Text Analysis", "Machine Learning/Deep Learning", 
                    "Geospatial Data, Tools and Libraries", "Web Development (Front-end, Back-end, Full stack)", 
                    "Mobile App Development", "Cloud Computing"]

                    

        for i, e in enumerate(skills):

            Question.objects.create(
                project = instance,
                question_num = i + 1,
                question_text = "Please rate your technical experience with {}.".format(e),
                question_type = 'dropdown',
                question_data = "No experience;Beginner;Familiar;Intermediate;Advanced"

            )

