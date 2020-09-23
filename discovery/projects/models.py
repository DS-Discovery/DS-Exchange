from django.db import models



class Partner(models.Model):
    email_address = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)


    project_name = models.CharField(max_length=200)

    project_category = models.CharField(max_length=100)
    student_num = models.IntegerField(default=0)
    description = models.CharField(max_length=5000)

    def __str__(self):
        return self.project_name
