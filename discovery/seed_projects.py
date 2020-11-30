"""
seed Project objects into local database
using partner csv file
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django
django.setup()

from projects.models import Project
import pandas as pd


if __name__ == "__main__":
    path = "csv/partner_sp2020.csv"
    df = pd.read_csv(path)
    df = df[:48]
    for _, row in df.iterrows():
        project = Project(organization=row["Organization "],
                          project_name=row["Project name"],
                          project_category=row["Project Category"],
                          description=row[
                              "Please provide a brief description for your project that we can list on our website."],
                          )
        project.save()
