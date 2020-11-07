from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from students.models import Student
from projects.models import Partner

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

            full_name = form.cleaned_data['full_name']
            sid = form.cleaned_data['student_id']
            college = form.cleaned_data['college']
            major = form.cleaned_data['major']
            year = form.cleaned_data['year']

            s = Student(email_address = email, full_name = full_name,
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
        print(email)
        student = Student.objects.filter(email_address = email)
        form = EditStudentSignupForm(request.POST)
        if form.is_valid():

            student.update(full_name = form.cleaned_data['full_name'])
            student.update(college = form.cleaned_data['college'])
            student.update(major = form.cleaned_data['major'])
            student.update(year = form.cleaned_data['year'])
            return HttpResponseRedirect('/student/profile')

    else: 
        data = Student.objects.get(email_address = email).__dict__
        form = EditStudentSignupForm(initial = data)




    return render(request, 'account/studentProfileEdit.html', {'title' : "Student Edit Profile", 'form' : form})

@login_required
def studentProfileView(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    studentExists = Student.objects.filter(email_address = email).exists()

    if not studentExists:
        return HttpResponseRedirect("/student/signup")


    context = Student.objects.get(email_address = email).__dict__
    print(context)
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
            partner.update(organization = form.cleaned_data['organization'])
            partner.update(project_name = form.cleaned_data['project_name'])
            partner.update(project_category = form.cleaned_data['project_category'])
            partner.update(student_num = form.cleaned_data['student_num'])
            partner.update(description = form.cleaned_data['description'])

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

    context = Partner.objects.get(email_address = email).__dict__
    print(context)
    return render(request, 'login/partnerBasic.html', {'context' : context})

@login_required
def redirectProfile(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    if User.objects.filter(email = email, groups__name = "Partner").exists():
        return HttpResponseRedirect('/partner/profile')
    return HttpResponseRedirect('/student/profile')