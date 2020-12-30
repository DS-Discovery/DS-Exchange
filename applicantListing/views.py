from django.shortcuts import render
from students.models import Student
from projects.models import Partner, Project
from applications.models import Application
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404

# Create your views here.

# # default project
# PROJECT_ID = 98

@login_required
def index(request):
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
