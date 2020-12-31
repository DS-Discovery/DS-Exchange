from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from applications.models import Answer, Application
from projects.models import Project, Question


def get_default_skills():
    return {
        "R": "",
        "Python": "",
        "data visualization": "",
        # etc.
    }


class Student(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    college_choices = (
        ('College Letters & Science','College Letters & Science'),
        ('College of Engineering','College of Engineering'),
        ('College of Chemistry', 'College of Chemistry'),
        ('College of Environmental Design','College of Environmental Design'),
        ('Rausser College of Natural Resources','Rausser College of Natural Resources'),
        ('Haas School of Business','Haas School of Business'),
    )

    skill_levels_options = {
        "": "",
        "NE": "No experience",
        "BE": "Beginner",
        "FA": "Familiar",
        "IN": "Intermediate",
        "AD": "Advanced",
    }

    skill_levels_inverse = {v: k for k, v in skill_levels_options.items()}
    
    skill_levels = skill_levels_options.items()

    default_skills = get_default_skills()

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
    general_question = models.CharField(max_length=2000, null = True, blank=True)

    _skills = models.JSONField(default=get_default_skills, null=False)

    @property
    def skills(self):
        d = self.default_skills.copy()
        d.update(self._skills)
        for s in d:
            try:
                d[s] = self.skill_levels_options[d[s]]
            except KeyError:
                d[s] = ""
        return d

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.email_address
