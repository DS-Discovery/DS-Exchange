import django
django.setup()

import pandas as pd
from projects.models import Partner
from students.models import Student

# path = "partner_sp2020.csv"
#
# df = pd.read_csv(path)
# df = df[:48] # remove incompletes
#
# for indx, row in df.iterrows():
#     _, created = Partner.objects.get_or_create(
#         email_address= row['Email Address'],
#         first_name = row['First name'],
#         last_name = row['Last name'],
#         organization = row['Organization '],
#         project_name = row['Project name'],
#         project_category = row['Project Category'],
#         student_num = row['How many student researchers (8-10 hrs/week) do you anticipate needing?'],
#         description = row['Please provide a brief description for your project that we can list on our website.']
#     )

path = "student_sp2020.csv"

df = pd.read_csv(path)

for indx, row in df.iterrows():
    _, created = Student.objects.get_or_create(
        email_address=row['Email Address'],
        full_name = row['Full Name'],
        student_id = row['Student ID Number'],
        college = row['Which college are you enrolled in?'],
        major = row['What is your intended or declared major(s)/minor(s)?'],
        year = row['What is your expected graduation year?'],
        first_choice = row['1) What is your FIRST choice?'],
        second_choice = row['2) What is your SECOND choice?'],
        third_choice = row['3) What is your THIRD choice?']
    )
