from django.shortcuts import render
from students.models import Student
from projects.models import Project
from applications.models import Application

# Create your views here.

# default project
PROJECT_ID = 98


def index(request):
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

    if skill_wanted == "None":
        applications = Application.objects.filter(project_id=PROJECT_ID)
    else:
        print("skill_wanted: ", skill_wanted)
        print("level_wanted: ", level_wanted)


        for short in Student.skill_levels_options:
            if Student.skill_levels_options[short] == level_wanted:
                print(short)
                applications = Application.objects.filter(project_id=PROJECT_ID).filter(
                    student___skills__contains={skill_wanted: short})
                break
    #print("hi")
    #print(applications)

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
