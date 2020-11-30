"""
seed Application objects into local database,
assigning corresponding project_id according
to project records
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django

django.setup()

from students.models import Student
from projects.models import Project
from applications.models import Application
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd

if __name__ == "__main__":
    path = "csv/student_sp2020.csv"
    df = pd.read_csv(path)

    # find corresponding Student
    try:
        student = Student.objects.get(email_address=row["Email Address"])
    except ObjectDoesNotExist:
        continue

    for _, row in df.iterrows():
        # find corresponding Project

        choices = []
        choices.append(row["1) What is your FIRST choice?"])
        choices.append(row["2) What is your SECOND choice?"])
        choices.append(row["3) What is your THIRD choice?"])

        for i in range(3):

            try:
                project = Project.objects.get(project_name=choices[i])


                application = Application(student=student,
                                          project=project,
                                          rank=i+1,
                                          status="SENT",
                                          )

                application.save()

            except ObjectDoesNotExist:
                continue
