from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from students.models import Student
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView

from .forms import StudentSignupForm

from .forms import EditStudentSignupForm



from django.contrib.auth import update_session_auth_hash

def index(request):
    return HttpResponse("Login View")





def view_profile(request, pk=None):
    if pk:
        user = Student.objects.get(pk=pk)
    else:
        user = request.user
    args = {'user': user}
    return render(request, 'accounts/profile.html', args)

def edit_profile(request):
    if request.method == 'POST':
        form = EditStudentProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('accounts:view_profile'))
    else:
        form = EditStudentProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)


@login_required
def student_signup(request):
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
            email = username
            full_name = form.cleaned_data['full_name']
            sid = form.cleaned_data['student_id']
            college = form.cleaned_data['college']
            major = form.cleaned_data['major']
            year = form.cleaned_data['year']

            s = Student(email_address = email, full_name = full_name,
                         student_id = sid, college = college, major = major, year = year)
            # print(s)
            s.save()

        # return HttpResponseRedirect('/submitted')
    else: # GET
        form = StudentSignupForm()



    return render(request, 'account/studentSignup.html', {'title' : "Student Create Profile",'form' : form})

@login_required
def student_profile_edit(request):
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
    

    else: 
        form = EditStudentSignupForm()




    return render(request, 'account/studentSignup.html', {'title' : "Student Edit Profile", 'form' : form})

@login_required
def studentProfileView(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    context = Student.objects.get(email_address = email).__dict__
    print(context)
    return render(request, 'login/studentBasic.html', {'context' : context})


def partnerProfileView(request):
    pass
    # return render(request, 'login/partnerBasic.html')