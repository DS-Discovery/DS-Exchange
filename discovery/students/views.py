from django.shortcuts import render
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf

from students.forms import studentForm
from students.forms import AnswerForm

from .models import Student
from .models import Question
from projects.models import Partner
# Create your views here.
from django.http import HttpResponse


def index(request):
    # question_list = Question.objects
    # context = {'question_list': question_list}
    # return render(request, 'students/index.html', context)
    return HttpResponse("hi")

def detail(request, project_name):
    try:
        partner = Partner.objects.get(project_name=project_name)
        print(partner, project_name)
        # print([e.project_name for e in Partner.objects.all()])
        questions = Question.objects.filter(partner = partner)
        # questions = question.objects.get(project_name = project)

    except Question.DoesNotExist:
        raise Http404("Question does not exist")

    if request.method == 'POST':
        form = AnswerForm(request.POST)

        for question in questions:
            print(question.id)
            print(request.POST)
            print(request.POST[str(question.id)])

        if form.is_valid:
            form.save()
            return HttpResponseRedirect('/submitted')
    else: # GET
        form = AnswerForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    print(partner, questions)
    return render(request, 'students/detail.html', {'questions': questions, 'partner' : partner})


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
