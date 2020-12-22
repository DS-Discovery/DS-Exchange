from django.shortcuts import render
from students.models import Student
from projects.models import Project
from applications.models import Application

# Create your views here.

# default project
PROJECT_ID = 35

def index(request):

    applicant_num = 0
    if request.method == "POST":
        applicant_num = int(request.POST.get("selected_applicant")) - 1

    project = Project.objects.filter(id=PROJECT_ID)
    applications = Application.objects.filter(project_id=PROJECT_ID)
    print("HELLO")
    print(applications)
    student = applications[applicant_num].student

    context = {
        "num_apps": range(1, len(applications) + 1),
        "curr_app": applications[applicant_num],
        "curr_student": student
    }

    return render(request, 'applicant_listing.html', context)
