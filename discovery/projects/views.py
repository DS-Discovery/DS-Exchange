from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Partner


def index(request):
    if request.method == 'POST':
        category = request.POST.get('category_wanted')
        latest_question_list = Partner.objects.filter(project_category__contains=category)
    else:
        latest_question_list = Partner.objects.order_by('project_name')
    project_category_list = set()
    for e in Partner.objects.all():
        categories = e.project_category.strip().split(',')
        categories = [cat.strip() for cat in categories]
        project_category_list.update(categories)
    project_category_list = sorted(list(project_category_list))
    context = {'latest_question_list': latest_question_list,
                'project_category_list': project_category_list}
    return render(request, 'projects.html', context)


def detail(request, project_name):
    try:
        project = Partner.objects.get(project_name=project_name)
    except Partner.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'project.html', {'project': project})
