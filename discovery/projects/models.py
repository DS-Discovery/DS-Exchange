from django.db import models



class Partner(models.Model):
    email_address = models.EmailField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    organization = models.CharField(max_length=20)
    project_name = models.CharField(max_length=50)
    project_category = models.CharField(max_length=50)
    student_num = models.IntegerField(default=0)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.project_name
