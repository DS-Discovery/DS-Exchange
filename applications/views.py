from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import Http404, redirect, render

from applications.models import Answer, Application
from projects.models import Partner, Project
from students.models import Student


def model_list_to_dict(l):
    return {m.id: m.to_dict() for m in l}


@login_required
def get_applications(request):
    if request.user.is_authenticated:
        email = request.user.email
    else:
        raise PermissionDenied("User is not authenticated")

    if Student.objects.filter(email_address = email).exists():
        return list_student_applications(request)
    elif Partner.objects.filter(email_address = email).exists():
        return list_project_applicants(request)
    else:
        messages.info(request, "Please create your student profile to view applications.")
        return redirect("/profile")


@login_required
def list_student_applications(request):
    # email = EMAIL_ADDRESS
    if request.user.is_authenticated:
        email = request.user.email
    else:
        raise PermissionDenied("User is not authenticated")

    student = Student.objects.get(email_address = email)

    # changed from email to student
    # all_apps = Application.objects.filter(email_address=EMAIL_ADDRESS)
    first_project, second_project, third_project = None, None, None
    all_apps = Application.objects.filter(student = student).order_by("created_at")
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

    partner = Partner.objects.get(email_address = email)

    projects = [ppi.project for ppi in partner.partnerprojectinfo_set.all()]
    # project_wanted = request.GET.get("project_wanted")
    # if project_wanted is not None:
    #     project_wanted = Project.objects.get(id=project_wanted)
    #     if project_wanted not in projects:
    #         messages.info("You do not have permission to view this project.")
    #         return redirect("/applications")
    # else:
    if len(projects) == 0:
        messages.info("You do not have any projects assigned to you. If this is an error, please contact ds-discovery@berkeley.edu.")
        return redirect("/")
        # project_wanted = projects[0]

    applications = Application.objects.filter(project__in=projects)
    students = Student.objects.filter(email_address__in=applications.values_list("student", flat=True))
    print(applications, students, projects)

    projects, applications, students = model_list_to_dict(projects), model_list_to_dict(applications), model_list_to_dict(students)

    skills = list(Student.default_skills.keys())
    skills.insert(0, "None")
    levels = list(Student.skill_levels_options.values())

    # skill_wanted = "None"
    # level_wanted = "No experience"
    
    # if request.GET.get("skill_wanted"):
    #     skill_wanted = request.GET.get("skill_wanted")

    # if request.GET.get("level_wanted"):
    #     level_wanted = request.GET.get("level_wanted")

    # selected_applicant = None
    # if request.GET.get("selected_applicant"):
    #     selected_applicant = request.GET.get("selected_applicant")

    # if skill_wanted == "None":
    #     applications = Application.objects.filter(project_id=project_wanted.id).order_by("created_at")
    
    # else:
    #     print("skill_wanted:", skill_wanted)
    #     print("level_wanted:", level_wanted)

    #     for short in Student.skill_levels_options:
    #         if Student.skill_levels_options[short] == level_wanted:
    #             print(short)
    #             applications = Application.objects.filter(project_id=project_wanted.id).filter(
    #                 student___skills__contains={skill_wanted: short}
    #             )
    #             break

    # if not applications or selected_applicant is None:
    #     student = None
    #     curr_app = None
    
    # else:
    #     student = Application.objects.get(id=selected_applicant).student
    #     curr_app = Application.objects.get(id=selected_applicant)
    #     print("curr_app:", curr_app)

    #     answers = Answer.objects.filter(student=student, application=curr_app)

    # context = {
    #     "num_apps": range(len(applications)),
    #     "curr_app": curr_app,
    #     "curr_student": student,
    #     "skills": skills,
    #     "skill_wanted": skill_wanted,
    #     "levels": levels,
    #     "level_wanted": level_wanted,
    #     "applications": applications,
    #     "projects": projects,
    #     "project_wanted": project_wanted,
    # }

    # if curr_app is not None:
    #     context.update({
    #         "questions_and_answers": zip([a.question for a in answers], answers),
    #     })

    context = {
        "applications_json": {
            "projects": projects,
            "applications": applications,
            "students": students,
            "skills": skills,
            "levels": levels,
        }
    }

    return render(request, 'applications/review_applicants.html', context)


@login_required
def update_application_status(request):
    if request.method == "GET":
        raise SuspiciousOperation("This is a POST-only route.")

    email = None
    if request.user.is_authenticated:
        email = request.user.email

    try:
        partner = Partner.objects.get(email_address = email)
    except ObjectDoesNotExist:
        return HttpResponse("You do not have permission to perform this action.", status=403)

    application_id = request.POST.get("application_id")
    new_status = request.POST.get("new_status")
    if application_id is None or new_status not in [t[0] for t in Application.ApplicationStatus.choices]:
        return HttpResponse("Improperly formed request. Please try again or contact ds-discovery@berkeley.edu", status=400)

    application = Application.objects.get(id=application_id)

    partner_projects = [ppi.project for ppi in partner.partnerprojectinfo_set.all()]
    if application.project not in partner_projects:
        # messages.info(request, "You do not have permission to update this application.")
        # return redirect("/applications")
        return HttpResponse("You do not have permission to perform this action.", status=403)

    application.status = new_status
    application.save()

    return HttpResponse("Application status successfully updated.", status=200)

    # messages.info(request, "Application status successfully updated.")
    # return redirect(
    #     f"/applications?selected_applicant={application.id}&project_wanted={application.project.id}"
    #     f"&skill_wanted={request.POST.get('skill_wanted')}&level_wanted={request.POST.get('level_wanted')}"
    # )
