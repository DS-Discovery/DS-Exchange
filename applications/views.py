from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404, render

from applications.models import Application
from projects.models import Partner, Project
from students.models import Student


@login_required
def index(request):
    # email = EMAIL_ADDRESS
    if request.user.is_authenticated:
        email = request.user.email
    else:
        return Http404("Student is not authenticated")
    # email = EMAIL_ADDRESS # set to default
    student = Student.objects.get(email_address = email)
    print("student", student)

    # changed from email to student
    # all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    first_project, second_project, third_project = None, None, None
    all_apps = Application.objects.filter(student = student)
    print("all_apps", all_apps)
    if len(all_apps) == 3:
        first_project = Project.objects.get(id=all_apps[0].project_id)
        second_project = Project.objects.get(id=all_apps[1].project_id)
        third_project = Project.objects.get(id=all_apps[2].project_id)
    elif len(all_apps) == 2:
        first_project = Project.objects.get(id=all_apps[0].project_id)
        second_project = Project.objects.get(id=all_apps[1].project_id)
    elif len(all_apps) == 1:
        first_project = Project.objects.get(id=all_apps[0].project_id)


    num_apps = range(1, len(all_apps) + 1)
    
   
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


@login_required
def list_project_applicants(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    try:
        partner = Partner.objects.get(email_address = email)
    except ObjectDoesNotExist:
        raise Http404("you are not a partner")

    skills = list(Student.default_skills.keys())
    skills.insert(0, "None")
    levels = list(Student.skill_levels_options.values())
    levels = levels[1:]

    skill_wanted = "None"
    level_wanted = "No experience"
    if request.GET.get("skill_wanted"):
        skill_wanted = request.GET.get("skill_wanted")

    if request.GET.get("level_wanted"):
        level_wanted = request.GET.get("level_wanted")

    applicant_num = 0
    if request.method == "POST":
        applicant_num = int(request.POST.get("selected_applicant")) - 1

    #project = Project.objects.filter(id=PROJECT_ID)
    # projects
    # TODO: this needs to handle partners w/ multiple projects
    for ppi in partner.partnerprojectinfo_set.all():
        project = ppi.project

    # project = Project.objects.get(project_name=project_name)

    if skill_wanted == "None":
        applications = Application.objects.filter(project_id=project.id)
    else:
        print("skill_wanted: ", skill_wanted)
        print("level_wanted: ", level_wanted)


        for short in Student.skill_levels_options:
            if Student.skill_levels_options[short] == level_wanted:
                print(short)
                applications = Application.objects.filter(project_id=project.id).filter(
                    student___skills__contains={skill_wanted: short})
                break

    if not applications:
        student = None
        curr_app = None
    else:
        student = applications[applicant_num].student
        print(student._skills)
        curr_app = applications[applicant_num]
    # print(Student.skills)
    # for name, value in Student.skills.attributes().items():
    # print(name, value)

    context = {
        "num_apps": range(1, len(applications) + 1),
        "curr_app": curr_app,
        "curr_student": student,
        "skills": skills,
        "skill_wanted": skill_wanted,
        "levels": levels,
        "level_wanted": level_wanted,
    }

    return render(request, 'applicant_listing.html', context)
