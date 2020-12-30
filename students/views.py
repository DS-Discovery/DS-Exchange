from django.shortcuts import render
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf

# from students.forms import studentForm
# from students.forms import AnswerForm

# from .models import Student
# from .models import Question
# from projects.models import Partner
# Create your views here.
from django.http import HttpResponse


def index(request):
    # question_list = Question.objects
    # context = {'question_list': question_list}
    # return render(request, 'students/index.html', context)
    return HttpResponse("This is the students index.")
