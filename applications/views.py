from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import Http404, redirect, render

from applications.models import Answer, Application
from projects.models import Partner, Project, PartnerProjectInfo
from students.models import Student


def model_list_to_dict(l):
    return {m.id: m.to_dict() for m in l}


@login_required
def get_applications(request):
    if request.user.is_authenticated:
        email = request.user.email
    else:
        raise PermissionDenied("User is not authenticated")

    if Partner.objects.filter(email_address = email).exists():
        return list_project_applicants(request)
    elif Student.objects.filter(email_address = email).exists():
        return list_student_applications(request)
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

    no_apps = len(all_apps) == 0
    # if len(all_apps) > 2:
    #     third_project = Project.objects.get(id=all_apps[2].project_id)
    # if len(all_apps) > 1:
    #     second_project = Project.objects.get(id=all_apps[1].project_id)
    # if len(all_apps) > 0:
    #     first_project = Project.objects.get(id=all_apps[0].project_id)
    #     no_apps = False
    # else:
    #     no_apps = True

    num_apps = list(range(0, len(all_apps)))

    context = {
        "num_apps": num_apps,
        # "active_project": first_project,
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

        app = all_apps[selected_application]
        context["selected_application"] = selected_application

        answers = Answer.objects.filter(student=student, application=app)
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
        messages.info(request, "You do not have any projects assigned to you. If this is an error, please contact ds-discovery@berkeley.edu.")
        return redirect("/")
        # project_wanted = projects[0]

    applications = Application.objects.filter(project__in=projects)
    students = Student.objects.filter(email_address__in=applications.values_list("student", flat=True))
    projectPartners = PartnerProjectInfo.objects.filter(project__in=projects)
    print(applications, students, projects, projectPartners)

    projects, applications, students, projectPartners = model_list_to_dict(projects), model_list_to_dict(applications), model_list_to_dict(students), model_list_to_dict(projectPartners)

    skills = list(Student.default_skills.keys())
    skills.insert(0, "None")
    levels = list(Student.skill_levels_options.values())

    context = {
        "applications_json": {
            "projects": projects,
            "applications": applications,
            "students": students,
            "skills": skills,
            "levels": levels,
            "projectPartners": projectPartners,
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
