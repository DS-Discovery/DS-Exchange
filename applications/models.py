from django.db import models
from django.utils.translation import gettext_lazy as _

from projects.models import Project, Question


class Application(models.Model):

    class ApplicationStatus(models.TextChoices):
        SUBMITTED = "SUB", _("Submitted")
        REJECTED_NO_INTERVIEW = "RNI", _("Rejected without interview")
        INTERVIEWED = "INT", _("Invite to interview")
        REJECTED_WITH_INTERVIEW = "RWI", _("Rejected after interview")
        OFFER_SENT =  "OFS", _("Offer sent")
        OFFER_REJECTED = "OFR", _("Offer rejected")
        OFFER_ACCEPTED = "OFA", _("Offer accepted")

    # primary key auto-generated by project model
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # for ordering applications
    created_at = models.DateTimeField(auto_now_add=True)

    # rank of each applied project
    rank = models.IntegerField(default=0)

    # application status, uses ApplicationStatus enum
    status = models.CharField(max_length=3, choices=ApplicationStatus.choices, default=ApplicationStatus.SUBMITTED)

    @property
    def app_status_choices(self):
        return {k: v for k, v in self.ApplicationStatus.choices}

    @property
    def possible_next_statuses(self):
        if self.status == "SUB":
            return ["RNI", "INT"]
        elif self.status == "INT":
            return ["RWI", "OFS"]
        elif self.status == "OFS":
            return ["OFR", "OFA"]
        return []

    def __str__(self):
        return self.student.email_address + " application for " + self.project.project_name


class Answer(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE) # PRIMARY KEY
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.answer_text
