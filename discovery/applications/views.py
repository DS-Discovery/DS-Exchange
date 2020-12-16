from django.shortcuts import render, Http404
from projects.models import Project, Partner
from applications.models import Application
from students.models import Student

# default student email for testing
EMAIL_ADDRESS = "22szavala@berkeley.edu"

def index(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    else:
        return Http404("Student is not authenticated")
    student = Student.objects.get(email_address = email)
    # print(student)

    # changed from email to student
    # all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    all_apps = Application.objects.filter(student = student)
    print(all_apps)

    num_apps = range(1, len(all_apps) + 1)
    
    first_project = Project.objects.get(id=all_apps[0].project_id)
    second_project = Project.objects.get(id=all_apps[1].project_id)
    third_project = Project.objects.get(id=all_apps[2].project_id)
    context = {"num_apps": num_apps,
               "active_project": first_project,
    }

    context["active_application"] = None
    selected_status = None

    if request.method == "POST":
        # here when select dropdown category
        selected_application = request.POST.get('selected_application')
        if selected_application == "first_project":
            context["active_project"] = first_project
            context["active_application"] = all_apps[0]
        elif selected_application == "second_project":
            context["active_project"] = second_project
            context["active_application"] = all_apps[1]
        elif selected_application == "third_project":
            context["active_project"] = third_project
            context["active_application"] = all_apps[2]
        else:
            context["active_project"] = first_project
            context["active_application"] = all_apps[0]


        selected_status = request.POST.get('selected_status')
        if selected_status:
            context["selected_status"] = selected_status
            context["active_application"].status = selected_status
            context["active_application"].save()

    selected_partner = None
    for partner in Partner.objects.all():
        projects = partner.projects.all()
        if context["active_project"] in projects:
            selected_partner = partner
    context["selected_partner"] = selected_partner

    if not context["active_application"]:
        context["active_project"] = first_project
        context["active_application"] = all_apps[0]
    if context["active_application"].status != "SENT":
        context["available_status"] = ["Accept Offer", "Reject Offer"]
    else:
        context["available_status"] = ["NA"]
    # else:
    #     context["available_status"] = ["NA"]
    #     context["active_project"] = first_project
    #     context["active_application"] = all_apps[0]

    # print(context)
    # if context["active_application"]:
    #     print(context["active_application"].status)
    return render(request, "application_listing.html", context=context)

def getProject(request):
   print("INSIDE GETPROJECT")