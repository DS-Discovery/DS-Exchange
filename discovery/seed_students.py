"""
seed Student objects into local database
using partner csv file
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "discovery.settings")

import django
django.setup()

from students.models import Student
#from django.db.utils.DataError
import pandas as pd

if __name__ == "__main__":
    path = "csv/student_sp2020.csv"
    df = pd.read_csv(path)


    for _, row in df.iterrows():

        # general question field too long for this student
        if (row["Email Address"] == "saad.jamal@berkeley.edu"):
            continue
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
                          )
        student.save()
