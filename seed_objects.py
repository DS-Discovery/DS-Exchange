"""
seed student, project, application
objects into local postgres
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django
django.setup()


from students.models import Student
from projects.models import Project, Partner
from applications.models import Application
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd

student_path = "student_sp2020.csv"
partner_path = "partner.csv"

if __name__ == "__main__":
    df_student = pd.read_csv(student_path)
    df_partner = pd.read_csv(partner_path)

    # make sure all tables are empty
    Student.objects.all().delete()
    Project.objects.all().delete()
    Application.objects.all().delete()

    # seeding students
    for _, row in df_student.iterrows():
        # general question field too long for this student
        if (row["Email Address"] == "saad.jamal@berkeley.edu"):
            continue

        skills = []
        responses = [
            row["What is your experience with the following programming languages, tools, and skills? [Python]"],
            row["What is your experience with the following programming languages, tools, and skills? [R]"],
            row["What is your experience with the following programming languages, tools, and skills? [Data Vizualization (Pyplot, Seaborn, etc.)]"],
        ]

        for resp in responses:
            if resp == "No experience":
                skills.append("NE")
            elif resp == "Beginner (I can do a few operations)":
                skills.append("BE")
            elif resp == "Familiar (I have developed at least one project)":
                skills.append("FA")
            elif resp == "Intermediate (Multiple semesters of experience)":
                skills.append("IN")
            elif resp == "Advanced (I would feel comfortable teaching the subject)":
                skills.append("AD")
            else:
                skills.append("")

        R_skill = skills[0]
        python_skill = skills[1]
        data_viz_skill = skills[2]

        _skills = {
            "R": R_skill,
            "Python": python_skill,
            "data visualization": data_viz_skill,
        }


        student = Student(email_address=row["Email Address"],
                          first_name=row["Full Name"].split()[0],
                          last_name=row["Full Name"].split()[-1],
                          student_id=row["Student ID Number"],
                          college=row["Which college are you enrolled in?"],
                          major=row["What is your intended or declared major(s)/minor(s)?"],
                          year=row["What is your expected graduation year?"],
                          first_choice=row["1) What is your FIRST choice?"],
                          second_choice=row["2) What is your SECOND choice?"],
                          third_choice=row["3) What is your THIRD choice?"],
                          resume_link=row["Please attach your resume."],
                          general_question=row["Is there any other information you would like us to consider?"],
                          _skills=_skills,
                          )
        student.save()

    # seeding projects
    for _, row in df_partner.iterrows():
        project = Project(organization=row["Organization "],
                          project_name=row["Project name"],
                          project_category=row["Project Category"],
                          description=row[
                              "Please provide a brief description for your project that we can list on our website."],
                          archived=row['Archived'],
                          semester="SP21", #TODO: default value.
                          )
        project.save()

        try:
          partner_object, created = Partner.objects.get_or_create(
              email_address=row['Email Address'],
              first_name = row['First name'],
              last_name = row['Last name']
          )
          # if not created:
          #     partner_object.first_name = row['First name']
          #     partner_object.last_name = row['Last name']
          partner_object.projects.add(project)


          print("partner_object", partner_object)
          print("partner_created", created)
        except:
          pass


    # seeding applications
    for _, row in df_student.iterrows():
        # find corresponding Student
        try:
            student = Student.objects.get(email_address=row["Email Address"])
        except ObjectDoesNotExist:
            continue

        choices = []
        choices.append(row["1) What is your FIRST choice?"])
        choices.append(row["2) What is your SECOND choice?"])
        choices.append(row["3) What is your THIRD choice?"])

        for i in range(3):
            # find corresponding Project
            try:
                project = Project.objects.get(project_name=choices[i])
                application = Application(student=student,
                                          project=project,
                                          rank=i+1,
                                          status="SUB",
                                          )
                application.save()
            except ObjectDoesNotExist:
                continue