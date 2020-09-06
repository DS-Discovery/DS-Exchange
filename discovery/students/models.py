from django.db import models


class Student(models.Model):
    email_address = models.EmailField()
    full_name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    major = models.CharField(max_length=50)
    year = models.CharField(max_length=20)
    first_choice = models.CharField(max_length=50)
    second_choice = models.CharField(max_length=50)
    third_choice = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name
