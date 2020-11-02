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


def index(request):
    if request.method == 'POST':
        # here when select dropdown category
        category = request.POST.get('category_wanted')
        project = request.POST.get('project_wanted')
        print(request.POST)
        print("project_wanted is", project)
        if category:
            latest_question_list = Partner.objects.filter(project_category__contains=category)
        else:
            latest_question_list = Partner.objects.order_by('project_name')
    else:
        latest_question_list = Partner.objects.order_by('project_name')

    project_category_list = set()
    for e in Partner.objects.all():
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
            context["selected_project"] = Partner.objects.filter(project_name=project)[0]

    else:
        context = {'latest_question_list': latest_question_list,
                   'project_category_list': project_category_list,
                   }

    print("selected project", context["selected_project"])
    return render(request, 'projects.html', context)


def detail(request, project_name):
    try:
        partner = Partner.objects.get(project_name=project_name)
        print(partner, project_name)
        # print([e.project_name for e in Partner.objects.all()])
        questions = Question.objects.filter(partner = partner)
        # questions = question.objects.get(project_name = project)

    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'project.html', {'project': project})


def app(request, project_name):
        # this view shows the project name as well as the project questions
        # need to add user authentication


    # check to see if that partner project exists, if so, get the questions for it
        try:
            partner = Partner.objects.get(project_name=project_name)
            print(partner, project_name)

            questions = Question.objects.filter(partner = partner)


        except Question.DoesNotExist:
            raise Http404("Question does not exist")


        #if this form is submitted, then we want to save the answers
        if request.method == 'POST':

            email = None
            if request.user.is_authenticated:
                email = request.user.email
            student = Student.objects.get(email_address = email)
            print(student)

            for question in questions:
                print(question.id)
                print(request.POST)
                print(request.POST[str(question.id)])
                form = AnswerForm(request.POST)
                if form.is_valid():

                    print("form", form)

                    a = Answer(student = student, question = question, answer_text = form.cleaned_data[str(question.id)])
                    print(a)
                    a.save()
                return HttpResponseRedirect('/submitted')
        else: # GET
            form = AnswerForm()

        args = {}
        args.update(csrf(request))
        args['form'] = form
        print(partner, questions)


        return render(request, 'projects/detail.html', {'questions': questions, 'partner' : partner, 'form' : form})


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
