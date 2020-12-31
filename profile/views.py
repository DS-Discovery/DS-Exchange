from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from students.models import Student
from projects.models import Partner, PartnerProjectInfo

from .forms import EditPartnerSignupForm, EditStudentSignupForm, StudentSignupForm


@login_required
def student_signup(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    student = Student.objects.filter(email_address = email)

    if len(student) > 0:
        messages.info(request, 'You have already signed up.')
        return redirect('/profile')

    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            
            s = Student(
                email_address = email, 
                first_name = form.cleaned_data['first_name'], 
                last_name = form.cleaned_data['last_name'],
                student_id = form.cleaned_data['student_id'], 
                college = form.cleaned_data['college'], 
                major = form.cleaned_data['major'], 
                year = form.cleaned_data['year'], 
                resume_link= form.cleaned_data['resume_link'], 
                general_question = form.cleaned_data['general_question']
            )

            s.save()

            return redirect('/profile')

    else: 
        form = StudentSignupForm()
        return render(request, 'profile/edit_student_profile.html', {'title' : "Student Create Profile",'form' : form})


@login_required
def edit_student_profile(request):
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

            skills = student[0].skills
            for skill in skills:
                skills[skill] = form.cleaned_data.get(skill, "")

            student.update(_skills = skills)

            return redirect('/profile')

    else: 
        student = Student.objects.get(email_address = email)
        data = student.__dict__
        form = EditStudentSignupForm(initial = data)

        return render(request, 'profile/edit_student_profile.html', {
            'title' : "Student Edit Profile", 'form' : form, 'student': student, 'skills_tups': student.skills.items()
        })


@login_required
def view_student_profile(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    
    student_exists = Student.objects.filter(email_address = email).exists()

    if not student_exists:
        return redirect("/profile/signup")

    student = Student.objects.get(email_address = email)
    context = student.__dict__

    print(len(messages.get_messages(request)))

    return render(request, 'profile/student_profile.html', {'context' : context, "skills_tups": student.skills.items()})


# @login_required
# def partnerProfileEdit(request):
#     email = None
#     if request.user.is_authenticated:
#         email = request.user.email

#     if request.method == 'POST':
#         partner = Partner.objects.filter(email_address = email)

#         form = EditPartnerSignupForm(request.POST)
#         if form.is_valid():

#             partner.update(first_name = form.cleaned_data['first_name'])
#             partner.update(last_name = form.cleaned_data['last_name'])

#             return redirect('/partner/profile')

#     else: 
#         data = Partner.objects.get(email_address = email).__dict__
#         form = EditPartnerSignupForm(initial=data)

#     return render(request, 'profile/edit_partner_profile.html', {'title' : "Partner Edit Profile", 'form' : form})


@login_required
def view_partner_profile(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    context = Partner.objects.get(email_address = email)
    relationship = PartnerProjectInfo.objects.filter(partner = context)
   
    projects = [p.project for p in relationship]
    projectPartnerRoles = {}
    for p in projects:
        roles = PartnerProjectInfo.objects.filter(project = p)
        projectPartnerRoles[p.project_name] = roles

    return render(request, 'profile/partner_profile.html', {'context' : context.__dict__, 'projects': projects, 'projectPartnerRoles' : projectPartnerRoles})


@login_required
def get_profile(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    if User.objects.filter(email = email, groups__name = "Partner").exists():
        return view_partner_profile(request)
    return view_student_profile(request)


def google_auth_redirect(request):
    return redirect("/accounts/google/login")