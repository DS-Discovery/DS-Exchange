from django.shortcuts import render
from projects.models import Project, Partner
from applications.models import Application

# default student email for testing
EMAIL_ADDRESS = "22szavala@berkeley.edu"

def index(request):
    all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    num_apps = range(1, len(all_apps) + 1)
    
    first_project = Project.objects.get(id=all_apps[0].project_id)
    second_project = Project.objects.get(id=all_apps[1].project_id)
    third_project = Project.objects.get(id=all_apps[2].project_id)
    context = {"num_apps": num_apps,
               "active_project": first_project,
    }

    if request.method == "POST":
        # here when select dropdown category
        selected_application = request.POST.get('selected_application')
        if selected_application == "first_project":
        	context["active_project"] = first_project
        elif selected_application == "second_project":
        	context["active_project"] = second_project
        elif selected_application == "third_project":
        	context["active_project"] = third_project
    selected_partner = None
    for partner in Partner.objects.all():
        projects = partner.projects.all()
        if context["active_project"] in projects:
            selected_partner = partner
    context["selected_partner"] = selected_partner
   
    return render(request, "application_listing.html", context=context)

def getApp(request):
   return