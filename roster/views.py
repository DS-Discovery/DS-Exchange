
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import Http404, redirect, render

from applications.models import Answer, Application
from projects.models import Partner, Project, PartnerProjectInfo
from students.models import Student

@login_required
def display_student_team_roster(request):   
    email = None
    if request.user.is_authenticated:
            email = request.user.email
    else:
        raise PermissionDenied("User is not authenticated")  
   
    student = Student.objects.get(email_address = email)
    try:
        project = Application.objects.get(student = student, status= "OFA").project
    except:
        project = None

    context = {}
    context['isPartner'] = False 
    if project != None:
        context["project"] = project

        applications = Application.objects.filter(project=project)
        students = Student.objects.filter(email_address__in=applications.values_list("student", flat=True))
        projectPartners = PartnerProjectInfo.objects.filter(project=project)
        print(applications, students, project, projectPartners)

       
        context['students'] = students
        context['projectPartners'] = projectPartners
        
    else:
        context["project"] = project


    
    return render(request, "roster/roster.html", context=context)
    