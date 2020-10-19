from django.http import Http404
from django.shortcuts import render

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
        project = Partner.objects.get(project_name=project_name)
    except Partner.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'project.html', {'project': project})
