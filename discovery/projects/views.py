from django.http import Http404
from django.shortcuts import render
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf

from students.forms import AnswerForm

# from .models import Student
from .models import Question
from students.models import Answer
from .models import Partner
from students.models import Student
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Partner
from .models import Project

def index(request):
    if request.method == 'POST':
        # here when select dropdown category
        category = request.POST.get('category_wanted')
        project = request.POST.get('project_wanted')
        print(request.POST)
        print("project_wanted is", project)
        if category:
            latest_question_list = Project.objects.filter(project_category__contains=category)
        else:
            latest_question_list = Project.objects.order_by('project_name')
    else:
        latest_question_list = Project.objects.order_by('project_name')

    project_category_list = set()
    for e in Project.objects.all():
        categories = e.project_category.strip().split(',')
        categories = [cat.strip() for cat in categories]
        project_category_list.update(categories)
    project_category_list = sorted(list(project_category_list))


    # need to send requested category back to keep category selected
    if request.method == "POST":
        if category:
            context = {'latest_question_list': latest_question_list,
                       'project_category_list': project_category_list,
                       # send selected category back
                       'selected_category': request.POST.get("category_wanted")
                       }
        else:
            context = {'latest_question_list': latest_question_list,
                       'project_category_list': project_category_list,
                       }
        if project:
            context["selected_project"] = Project.objects.filter(project_name=project)[0]
            context["labels"] = context["selected_project"].project_category.split(",")

    else:
        context = {'latest_question_list': latest_question_list,
                   'project_category_list': project_category_list,
                   }

    # print("context", context)
    return render(request, 'projects.html', context)


def detail(request, project_name):
    try:
        project = Project.objects.get(project_name=project_name)
        print(project, project_name)
        # print([e.project_name for e in Partner.objects.all()])
        questions = Question.objects.filter(project = project)
        # questions = question.objects.get(project_name = project)

    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'project.html', {'project': project})


def app(request, project_name):
        # this view shows the project name as well as the project questions
        # need to add user authentication

    # check to see if that partner project exists, if so, get the questions for it
    try:
        project = Project.objects.get(project_name=project_name)
        questions = Question.objects.filter(project = project)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")


    #if this form is submitted, then we want to save the answers
    if request.method == 'POST':
        email = None
        if request.user.is_authenticated:
            email = request.user.email
        else:
            return Http404("Student is not authenticated")
        student = Student.objects.get(email_address = email)
        print(student)

        # for question in questions:
        #     print(question.id)
        #     print(request.POST)
        #     print(request.POST[str(question.id)])
        #     print("---------------------")

        #modify post request
        post = request.POST.copy()
        print(post)

        is_valid = True
        answer_text = ""
        keys = list(post.keys())
        for k in keys:
            if k == "csrfmiddlewaretoken":
                continue
            if len(post[k]) == 0:
                is_valid = False
            answer_text += str(k) + ". " + post[k] + " "
            post.pop(k)

        answer_text = answer_text.strip()
        if is_valid:
            post['answer_text'] = answer_text
        print(post)

        request.POST = post

        form = AnswerForm(request.POST)

        if form.is_valid():
            print("Is valid")
            a = Answer(student = student, question = project, answer_text = form.cleaned_data['answer_text'])
            a.save()
        else:
            print("not valid")
            print(form.errors)
        return HttpResponseRedirect('/submitted')
    else: # GET
        form = AnswerForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    # print(project, type(project))
    # print(questions)

    if request.user.is_authenticated:
        return render(request, 'projects/detail.html', {'questions': questions, 'project' : project, 'form' : form})
    else:
        raise Http404("User is not logged in")


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

    # def studentApplication(request):
    #     student_instance = get_object_or_404(Student)
    #
    #     if request.method == "POST":
    #
    #         form = studentApplication(request.POST)
    #         if form.is_valid():
    #             student_instance.first_name = form.cleaned_data['first_name']
    #
    #             student_instance.save()
    #
    #             return HttpResponse(reverse('index'))
    #     else:
    #         proposed_renewal_date = None
    #         form = studnetForm(initial={'first_name': proposed_renewal_date})
    #
    #     context = {
    #         'form': form,
    #         'student_instance': student_instance,
    #     }
    #
    #     return render(request, 'catalog/application.html', context)
