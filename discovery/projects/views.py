from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Partner


def index(request):
    latest_question_list = Partner.objects.order_by('project_name')
    context = {'latest_question_list': latest_question_list}
    return render(request, 'projects.html', context)


def detail(request, project_name):
    try:
        project = Partner.objects.get(project_name=project_name)
    except Partner.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'project.html', {'project': project})

