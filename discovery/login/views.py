from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from students.models import Student
from projects.models import Partner
from projects.models import PartnerProjectInfo

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView

from .forms import StudentSignupForm

from .forms import EditStudentSignupForm
from .forms import EditPartnerSignupForm
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import update_session_auth_hash

def index(request):
    return HttpResponse("Login View")



@login_required
def studentSignup(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    student = Student.objects.filter(email_address = email)
    print(student)
    if len(student) > 0:
        return
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            sid = form.cleaned_data['student_id']
            college = form.cleaned_data['college']
            major = form.cleaned_data['major']
            year = form.cleaned_data['year']

            s = Student(email_address = email, first_name = first_name, last_name = last_name,
                         student_id = sid, college = college, major = major, year = year)
            # print(s)
            s.save()

            return HttpResponseRedirect('/student/profile')

        # return HttpResponseRedirect('/submitted')
    else: # GET
        form = StudentSignupForm()



    return render(request, 'account/studentProfileEdit.html', {'title' : "Student Create Profile",'form' : form})

@login_required
def studentProfileEdit(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    if request.method == 'POST':
        print("Post request: ", request.POST)
        print("Email: ", email)
        student = Student.objects.filter(email_address = email)
        form = EditStudentSignupForm(request.POST)
        if form.is_valid():

            student.update(first_name = form.cleaned_data['first_name'])
            student.update(last_name = form.cleaned_data['last_name'])
            student.update(college = form.cleaned_data['college'])
            student.update(major = form.cleaned_data['major'])
            student.update(year = form.cleaned_data['year'])
            student.update(resume_link = form.cleaned_data['resume_link'])
            student.update(general_question = form.cleaned_data['general_question'])

            skills = student.skills
            for skill in skills:
                skills[skill] = form.cleaned_data.get(skill, "")

            student.update(_skills = skills)

            return HttpResponseRedirect('/student/profile')

    else: 
        student = Student.objects.get(email_address = email)
        data = student.__dict__
        form = EditStudentSignupForm(initial = data)




    return render(request, 'account/studentProfileEdit.html', {'title' : "Student Edit Profile", 'form' : form, 'student': student})

@login_required
def studentProfileView(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    studentExists = Student.objects.filter(email_address = email).exists()

    if not studentExists:
        return HttpResponseRedirect("/student/signup")


    context = Student.objects.get(email_address = email).__dict__
    # print(context)
    return render(request, 'login/studentBasic.html', {'context' : context})

@login_required
def partnerProfileEdit(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    if request.method == 'POST':
        print(email)
        partner = Partner.objects.filter(email_address = email)

        form = EditPartnerSignupForm(request.POST)
        if form.is_valid():

            partner.update(first_name = form.cleaned_data['first_name'])
            partner.update(last_name = form.cleaned_data['last_name'])

            return HttpResponseRedirect('/partner/profile')
  

    else: 
        data = Partner.objects.get(email_address = email).__dict__
        form = EditPartnerSignupForm(initial=data)

    return render(request, 'account/partnerProfileEdit.html', {'title' : "Partner Edit Profile", 'form' : form})






@login_required
def partnerProfileView(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    context = Partner.objects.get(email_address = email)
    # print(context.__dict__)
    # projects = context.projects.all()
    relationship = PartnerProjectInfo.objects.filter(partner = context)
   
    projects = [p.project for p in relationship]
    print("projects", projects)
    projectPartnerRoles = {}
    for p in projects:
        roles = PartnerProjectInfo.objects.filter(project = p)
        projectPartnerRoles[p.project_name] = roles
    print(projectPartnerRoles)
    return render(request, 'login/partnerBasic.html', {'context' : context.__dict__, 'projects': projects, 'projectPartnerRoles' : projectPartnerRoles})

@login_required
def redirectProfile(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    if User.objects.filter(email = email, groups__name = "Partner").exists():
        return HttpResponseRedirect('/partner/profile')
    return HttpResponseRedirect('/student/profile')