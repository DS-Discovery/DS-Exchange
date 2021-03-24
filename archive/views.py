import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, Http404, render, redirect
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from constance import config
from flags.state import flag_enabled

from applications.forms import AnswerForm
from applications.models import Answer, Application
from students.models import Student

from .forms import EditProjectForm
from projects.models import Partner, PartnerProjectInfo, Project, Question


logger = logging.getLogger(__name__)


# @login_required
def list_projects(request):
    # email = None
    # if request.user.is_authenticated:
    #     email = request.user.email

    # if email is None:
    #     return redirect('/profile/login')

    projects_json = get_projects_json()

    return render(request, 'projects/archive.html', {"projects_json": projects_json})


def get_projects_json():
    projects = []
    for p in Project.objects.all():
        d = p.to_dict()
        print(d['semester'])
        print(config.CURRENT_SEMESTER)
        if d['semester'] != config.CURRENT_SEMESTER:
            projects.append(d)

    projects = sorted(projects, key=lambda d: d["project_name"])

    return {"projects": projects}