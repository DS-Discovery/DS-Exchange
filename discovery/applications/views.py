from django.shortcuts import render
from projects.models import Project
from applications.models import Application

# default student email for testing
EMAIL_ADDRESS = "22szavala@berkeley.edu"

def index(request):
    all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    num_apps = range(1, len(all_apps) + 1)

    first_project = Project.objects.get(id=all_apps[0].project_id)

    context = {"num_apps": num_apps,
               "active_project": first_project,
    }
    return render(request, "application_listing.html", context=context)

def getProject(request):
   print("INSIDE GETPROJECT")