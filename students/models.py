from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from applications.models import Answer, Application
from projects.models import Project, Question, Semester


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
    }


class Student(models.Model):

    class College(models.TextChoices):
        LS = ("L&S", _("College of Letters & Sciences"))
        COE = ("COE", _("College of Engineering"))
        COC = ("COC", _("College of Chemistry"))
        CED = ("CED", _("College of Environmental Design"))
        CNR = ("CNR", _("Rausser College of Natural Resources"))
        HAAS = ("HAAS", _("Haas School of Business"))

    # college_choices = (
    #     ('College Letters & Science','College Letters & Science'),
    #     ('College of Engineering','College of Engineering'),
    #     ('College of Chemistry', 'College of Chemistry'),
    #     ('College of Environmental Design','College of Environmental Design'),
    #     ('Rausser College of Natural Resources','Rausser College of Natural Resources'),
    #     ('Haas School of Business','Haas School of Business'),
    # )

    egt_mapping = {k: v for k, v in Semester.choices}
    college_mapping = {k: v for k, v in College.choices}

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
    college = models.CharField(max_length=4, choices=College.choices)
    major = models.CharField(max_length=200)
    year = models.CharField(max_length=4, choices=Semester.choices)
    first_choice = models.CharField(max_length=1000, null=True, blank=True)
    second_choice = models.CharField(max_length=1000, null=True, blank=True)
    third_choice = models.CharField(max_length=1000, null=True, blank=True)

    resume_link = models.CharField(max_length=200, null = True, blank=True)
    general_question = models.CharField(max_length=1000, null = True, blank=True)

    additional_skills = models.CharField(max_length=300, null=True, blank=True)

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
    def id(self):
        return self.email_address

    @property
    def is_scholar(self):
        return DataScholar.objects.filter(email_address=self.email_address).exists()

    def to_dict(self):
        return {
            "email_address": self.email_address,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "student_id": self.student_id,
            "college": self.college_mapping[self.college],
            "major": self.major,
            "year": self.egt_mapping[self.year],
            "resume_link": self.resume_link,
            "general_question": self.general_question,
            "skills": self.skills,
            "additional_skills": self.additional_skills,
            "is_scholar": self.is_scholar,
        }

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.email_address


class DataScholar(models.Model):

    email_address = models.CharField(max_length=100, primary_key=True)
