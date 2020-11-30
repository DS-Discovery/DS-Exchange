from django.db import models
from students import models as student_models

# Create your models here.
class Application(models.Model):
    #email_address = models.EmailField(max_length=100, primary_key=True)
    email_address = models.EmailField(max_length=100)

    # primary key auto-generated by project model
    project_id = models.IntegerField()

    # rank of each applied project
    rank = models.IntegerField()

    status = models.CharField(max_length=100)