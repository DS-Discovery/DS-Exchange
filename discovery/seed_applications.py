"""
seed Application objects into local database,
assigning corresponding project_id according
to project records
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django

django.setup()

from projects.models import Project
from applications.models import Application
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd

if __name__ == "__main__":
    path = "csv/student_sp2020.csv"
    df = pd.read_csv(path)

    for _, row in df.iterrows():
        # find corresponding Project record and get id

        choices = []
        choices.append(row["1) What is your FIRST choice?"])
        choices.append(row["2) What is your SECOND choice?"])
        choices.append(row["3) What is your THIRD choice?"])

        for proj in choices:
            try:
                projObj = Project.objects.get(project_name=proj)
                proj_id = projObj.id

                application = Application(email_address=row["Email Address"],
                                          project_id=proj_id,
                                          status="SENT",
                                          )
                application.save()

            except ObjectDoesNotExist:
                continue
