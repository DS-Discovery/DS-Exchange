from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404, redirect, render

from applications.models import Application
from projects.models import Partner, Project
from students.models import Answer, Student


@login_required
def list_student_applications(request):
    # email = EMAIL_ADDRESS
    if request.user.is_authenticated:
        email = request.user.email
    else:
        return Http404("Student is not authenticated")
    # email = EMAIL_ADDRESS # set to default
    try:
        student = Student.objects.get(email_address = email)
    except ObjectDoesNotExist:
        return list_project_applicants(request)

    # changed from email to student
    # all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    first_project, second_project, third_project = None, None, None
    all_apps = Application.objects.filter(student = student)
    print("all_apps", all_apps)
    if len(all_apps) > 2:
        third_project = Project.objects.get(id=all_apps[2].project_id)
    if len(all_apps) > 1:
        second_project = Project.objects.get(id=all_apps[1].project_id)
    if len(all_apps) > 0:
        first_project = Project.objects.get(id=all_apps[0].project_id)
        no_apps = False
    else:
        no_apps = True

    num_apps = list(range(0, len(all_apps)))
   
    context = {
        "num_apps": num_apps,
        "active_project": first_project,
        "projects": [a.project for a in all_apps],
    }

    if not no_apps:

        context["active_application"] = None
        selected_status = None

        # if request.method == "POST":
            # here when select dropdown category
        selected_application = request.GET.get('selected_application')
        if selected_application is not None:
            selected_application = int(selected_application)
        else:
            selected_application = 0
        
        context["selected_application"] = selected_application
        if selected_application == 0:
            context["active_project"] = first_project
            context["active_application"] = all_apps[0]
        elif selected_application == 1:
            context["active_project"] = second_project
            context["active_application"] = all_apps[1]
        elif selected_application == 2:
            context["active_project"] = third_project
            context["active_application"] = all_apps[2]
        else:
            context["active_project"] = first_project
            context["active_application"] = all_apps[0]

            # selected_status = request.POST.get('selected_status')
            # if selected_status:
            #     context["selected_status"] = selected_status
            #     context["active_application"].status = selected_status
            #     context["active_application"].save()

        # selected_partner = None
        # for partner in Partner.objects.all():
        #     projects = partner.projects.all()
        #     if context["active_project"] in projects:
        #         selected_partner = partner
        # context["selected_partner"] = selected_partner

        if not context["active_application"] and all_apps:
            context["active_project"] = first_project
            context["active_application"] = all_apps[0]
        
        if context["active_application"] and context["active_application"].status != "SENT":
            context["available_status"] = ["Accept Offer", "Reject Offer"]
        
        else:
            context["available_status"] = ["NA"]

        if context["active_application"] is not None:
            answers = Answer.objects.filter(student=student, application=context["active_application"])
            context["questions_and_answers"] = zip([a.question for a in answers], answers)

    return render(request, "applications/student_applications.html", context=context)


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

    selected_applicant = None
    if request.GET.get("selected_applicant"):
        selected_applicant = request.GET.get("selected_applicant")

    #project = Project.objects.filter(id=PROJECT_ID)
    # projects
    # TODO: this needs to handle partners w/ multiple projects
    for ppi in partner.partnerprojectinfo_set.all():
        project = ppi.project

    # project = Project.objects.get(project_name=project_name)

    if skill_wanted == "None":
        applications = Application.objects.filter(project_id=project.id)
    
    else:
        print("skill_wanted:", skill_wanted)
        print("level_wanted:", level_wanted)

        for short in Student.skill_levels_options:
            if Student.skill_levels_options[short] == level_wanted:
                print(short)
                applications = Application.objects.filter(project_id=project.id).filter(
                    student___skills__contains={skill_wanted: short}
                )
                break

    if not applications or selected_applicant is None:
        student = None
        curr_app = None
    
    else:
        student = Application.objects.get(id=selected_applicant).student
        curr_app = Application.objects.get(id=selected_applicant)
        print("curr_app:", curr_app)

        answers = Answer.objects.filter(student=student, application=curr_app)

    context = {
        "num_apps": range(len(applications)),
        "curr_app": curr_app,
        "curr_student": student,
        "skills": skills,
        "skill_wanted": skill_wanted,
        "levels": levels,
        "level_wanted": level_wanted,
        "applications": applications,
    }

    if curr_app is not None:
        context.update({
            "questions_and_answers": zip([a.question for a in answers], answers),
        })

    print(context)

    return render(request, 'applications/review_applicants.html', context)
