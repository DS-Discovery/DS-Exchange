from django.shortcuts import render
from students.models import Student
from projects.models import Project
from applications.models import Application

# Create your views here.

# default project
PROJECT_ID = 249

def index(request):

    if request.method == "POST":
        print("posting")

    project = Project.objects.filter(id=PROJECT_ID)
    applications = Application.objects.filter(project_id=249)
    student = applications[0].student

    context = {
        "num_apps": range(1, len(applications) + 1),
        "curr_app": applications[0],
        "curr_student": student
    }

    return render(request, 'applicant_listing.html', context)
