
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django
django.setup()

import pandas as pd
from projects.models import Partner, Project
from students.models import Student

path = "partner_sp2020.csv"

df = pd.read_csv(path)
df = df[:48] # remove incompletes


for indx, row in df.iterrows():
    project_object, created = Project.objects.get_or_create(
        organization=row['Organization '],
        project_name=row['Project name'],
        project_category=row['Project Category'],
        student_num=row['How many student researchers (8-10 hrs/week) do you anticipate needing?'],
        description=row['Please provide a brief description for your project that we can list on our website.']
    )
    print("project_object", project_object)
    print("project_created", created)

    try:
        partner_object, created = Partner.objects.get_or_create(
            email_address=row['Email Address'],
            first_name = row['First name'],
            last_name = row['Last name']
        )
        # if not created:
        #     partner_object.first_name = row['First name']
        #     partner_object.last_name = row['Last name']
        partner_object.projects.add(project_object)


        print("partner_object", partner_object)
        print("partner_created", created)
    except:
        pass




path = "student_sp2020.csv"

df = pd.read_csv(path)

for indx, row in df.iterrows():
    if len(row['Full Name'].split()) == 2:
        first = row['Full Name'].split()[0]
        last = row['Full Name'].split()[1]
    else:
        first = " "
        last = " "

    student_object, created = Student.objects.get_or_create(
        email_address=row['Email Address'],
        first_name = first,
        last_name = last,
        student_id = row['Student ID Number'],
        college = row['Which college are you enrolled in?'],
        major = row['What is your intended or declared major(s)/minor(s)?'],
        year = row['What is your expected graduation year?'],
        first_choice = row['1) What is your FIRST choice?'],
        second_choice = row['2) What is your SECOND choice?']
    )

    print(student_object, student_object.first_name)
