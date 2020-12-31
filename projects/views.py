from django.http import Http404
from django.shortcuts import render, redirect
import datetime
import operator
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist

from students.forms import AnswerForm
from applications.forms import ApplicationForm
from django.contrib.auth.decorators import login_required

# from .models import Student
from .models import Question
from students.models import Answer
from .models import Partner
from students.models import Student
from applications.models import Application
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Partner
from .models import Project
from applications.models import Application
from .models import PartnerProjectInfo


from .forms import EditProjectForm


@login_required
def list_projects(request):
    # for category dropdown

    email = None
    if request.user.is_authenticated:
        email = request.user.email
    # student_exists = Student.objects.filter(email_address = email).exists()

    if email is None:
        return redirect('/profile/login')

    project_category_list = set()
    for e in Project.objects.all():
        categories = e.project_category.strip().split(',')
        categories = [cat.strip() for cat in categories]
        project_category_list.update(categories)

    project_category_list = sorted(list(project_category_list))
    latest_question_list = Project.objects.order_by('project_name')
    context = {
        'latest_question_list': latest_question_list,
        'project_category_list': project_category_list,
    }

    # need to send requested category back to keep category selected
    if request.GET.get('category_wanted') or request.GET.get('project_wanted'):
        
        # here when select dropdown category
        category = request.GET.get('category_wanted')
        project = request.GET.get('project_wanted')

        if category:
            # send selected category back
            context["selected_category"] = category
            latest_question_list = Project.objects.filter(project_category__contains=category)
            context["latest_question_list"] = latest_question_list

        if project:
            context["selected_project"] = Project.objects.filter(project_name=project)[0]
            
            selected_partner = None
            for partner in Partner.objects.all():
                projects = [p.project for p in partner.partnerprojectinfo_set.all()]
                if context["selected_project"] in projects:
                    selected_partner = partner
            
            context["selected_partner"] = selected_partner
            context["labels"] = context["selected_project"].project_category.split(",")

            context["num_applicants"] = len(Application.objects.filter(project=context["selected_project"]))

    return render(request, 'projects/listing.html', context)


# def detail(request, project_name):
#     try:
#         project = Project.objects.get(project_name=project_name)
#         print(project, project_name)
#         # print([e.project_name for e in Partner.objects.all()])
#         questions = Question.objects.filter(project = project)
#         # questions = question.objects.get(project_name = project)

#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'project.html', {'project': project})


@login_required
def apply(request, project_name):
    # this view shows the project name as well as the project questions
    # need to add user authentication

    # check to see if that partner project exists, if so, get the questions for it
    try:
        project = Project.objects.get(project_name=project_name)
        questions = Question.objects.filter(project = project).order_by('question_num')
    except Question.DoesNotExist:
        raise Http404("Question does not exist")

    email = None
    if request.user.is_authenticated:
        email = request.user.email
    else:
        messages.info("You must be logged in to apply to a project")
        return redirect('/')
    
    try:
        student = Student.objects.get(email_address = email)
    except ObjectDoesNotExist:
        if Partner.objects.filter(email_address = email).count() > 0:
            messages.info(request, "You must be a student to apply to projects.")
            return redirect("/projects")
        else:
            messages.info(request, "You have not yet signed up. Please complete the signup form to continue.")
            return redirect("/profile/signup")

    if student.first_choice and student.second_choice and student.third_choice:
        messages.info(request, 'You have already applied to 3 projects.')
        return redirect('/projects')

    count = Application.objects.filter(student = student, project = project).count()

    if count > 0:
        # raise Http404("Student already has an application submitted")
        messages.info(request, 'You have already applied to this project.')
        return redirect('/projects')

    #if this form is submitted, then we want to save the answers
    if request.method == 'POST':

        # student = Student.objects.get(email_address = email)
        # print(student)


   
        # neeed to check if student already submitted app before

        count = Application.objects.filter(student = student, project = project).count()

        if count > 0:
            # raise Http404("Student already has an application submitted")
            messages.info(request, 'You have already applied to this project.')
            return HttpResponseRedirect('/projects')



        # for question in questions:
        #     print(question.id)
        #     print(request.POST)
        #     print(request.POST[str(question.id)])
        #     print("---------------------")

        #modify post request

        post = request.POST.copy()
        print(post)


        def querydict_to_dict(query_dict):
            data = {}
            for key in query_dict.keys():
                v = query_dict.getlist(key)
                if len(v) == 1:
                    v = v[0]
                data[key] = v
            return data

        is_valid = True
        keys = list(post.keys())
        
        ans_list = []
        # creating individual answers
        for k in keys:
            if k == "csrfmiddlewaretoken":
                continue
            if len(post[k].strip()) == 0:
                is_valid = False
                break
            
            new_ans = request.POST.copy()
            new_ans_keys = list(new_ans.keys())
            q_num = 0
            answer_text = ""
            for new_k in new_ans_keys:
                if new_k == "csrfmiddlewaretoken":
                    continue
                if new_k == k:
                    q_num = new_k
                    # answer_text = post[new_k]
                    asDict = querydict_to_dict(post)
                    if type(asDict[k]) != list:
                        answer_text = asDict[k]
                    else:
                        answer_text = ";".join(asDict[k])
    
                new_ans.pop(new_k)

            new_ans['question_num'] = q_num
            new_ans['answer_text'] = answer_text
            ans_list.append(new_ans)

        if is_valid:

            try:
                application = Application.objects.get(student=student, project=project)
            except:
                 application = Application(student=student, project=project, status = "Sent")

            application.save()

            for post in ans_list:
                print(post)

                request.POST = post

                form = AnswerForm(request.POST)

                if form.is_valid():
                    print("Is valid")
                    
                    q_num = form.cleaned_data['question_num']

                    try:
                        a = Answer.objects.get(student=student, application=application, question_num=q_num)
                        a.answer_text = form.cleaned_data['answer_text']
                    except:
                        a = Answer(student=student, application = application, question_num = q_num,
                        answer_text = form.cleaned_data['answer_text'])
                    
                    a.save()
                else:
                    print("not valid")
                    print(form.errors)


            studentUpdater = Student.objects.filter(email_address = email)
            if not student.first_choice:
                studentUpdater.update(first_choice = project.project_name)
            elif not student.second_choice:
                studentUpdater.update(second_choice = project.project_name)
            elif not student.third_choice:
                studentUpdater.update(third_choice = project.project_name)
            else:
                # raise Http404("Student has applied to 3 applications")
                messages.info(request, 'You have already applied to 3 projects.')
                return HttpResponseRedirect('/projects')

            messages.info(request, 'Your application has been submitted successfully!')
            return HttpResponseRedirect('/projects')
        else:
            return HttpResponseRedirect(request.path_info)
    else: # GET
        form = AnswerForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    # print(project, type(project))
    # print(questions)

    if request.user.is_authenticated:
        print(questions)
        return render(request, 'projects/detail.html', {'questions': questions, 'project' : project, 'form' : form})
    else:
        raise Http404("User is not logged in")


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

@login_required
def partnerProjectView(request, project_name):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    try:
        context = Partner.objects.get(email_address = email)
    except ObjectDoesNotExist:
        raise Http404("you are not a partner")
    # projects = context.projects.all()
    # breakpoint()
    canView = False
    for ppi in context.partnerprojectinfo_set.all():
        project = ppi.project
        if project.project_name == project_name:
            canView = True
    if not canView:
        raise Http404("No permission")
    project = Project.objects.get(project_name=project_name)
    questions = Question.objects.filter(project = project).order_by('question_num')


    projectPartnerRoles = PartnerProjectInfo.objects.filter(project = project)

    return render(request, 'projects/partnerProjectView.html', {'questions': questions, 'project' : project, 'projectPartnerRoles': projectPartnerRoles})




@login_required
def partnerlisting(request):
    # for category dropdown
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    context = Partner.objects.get(email_address = email)
    roles = PartnerProjectInfo.objects.filter(partner = context)
    projects = [p.project for p in roles]

    # project_category_list = set()
    # for e in projects:
    #     categories = e.project_category.strip().split(',')
    #     categories = [cat.strip() for cat in categories]
    #     project_category_list.update(categories)
    # project_category_list = sorted(list(project_category_list))


    latest_question_list = projects
    context = {'latest_question_list': latest_question_list}

    # need to send requested category back to keep category selected
    if request.method == "POST":
        # here when select dropdown category
        
        project = request.POST.get('project_wanted')
        print("project_wanted is", project)
       
        if project:
            project = project.split("+")[0]
            

      
        if project:
            context["selected_project"] = Project.objects.filter(project_name=project)[0]
            # selected_partner = None
            # for partner in Partner.objects.all():
            #     projects = partner.projects.all()
            #     if context["selected_project"] in projects:
            #         selected_partner = partner
            # context["selected_partner"] = selected_partner
            context["labels"] = context["selected_project"].project_category.split(",")
            context['partnerProjectInfos'] = PartnerProjectInfo.objects.filter(project = context["selected_project"])
     
            questions = Question.objects.filter(project = context["selected_project"]).order_by('question_num')
            context['questions'] = questions
            context["count"] = len(Application.objects.filter(project =  context["selected_project"]))

    # print("context", context)
    # print("latest_question_list", latest_question_list)
    
    return render(request, 'projects/partnerListing.html', context)


# @login_required
# def editProjectProfile(request, project_name):
#     email = None
#     if request.user.is_authenticated:
#         email = request.user.email

#     if request.method == 'POST':

#         project = Project.objects.filter(id = request)

#         form = EditProjectForm(request.POST)
#         if form.is_valid():
#             project.update(organization = form.cleaned_data['organization'])
#             partner.update(project_name = form.cleaned_data['project_name'])
#             partner.update(project_category = form.cleaned_data['project_category'])
#             partner.update(student_num = form.cleaned_data['student_num'])
#             partner.update(description = form.cleaned_data['description'])

#             return HttpResponseRedirect('/project/profile')
#     else: 
#         data = Project.objects.get(project_name=project_name).__dict__
#         form = EditProjectForm(initial=data)

#     return render(request, 'projects/projectEdit.html', {'title' : "Project Edit Profile", 'form' : form})


# @login_required
# def editProjectQuestions(request):
#     email = None
#     if request.user.is_authenticated:
#         email = request.user.email
#     if User.objects.filter(email = email, groups__name = "Partner").exists():
#         pass
#     else:
#         return HttpResponse("Invalid credentials")


#     pass