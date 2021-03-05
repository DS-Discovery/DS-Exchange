import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

from students.models import Student
from projects.models import Partner, Project

class EditProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'project_name',
            'organization',
            'project_name',
            'project_category',
            'student_num',
            'description',            
            )


class PartnerProjCreationForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'email',
            'first_name',
            'last_name',
            'organization',
            'organization_description',
            'organization_website',
            'marketing_channel',
            'other_marketing_channel',
            'project_name',
            'project_category',
            'description',
            )

        labels = {
            "email": "Email address",
            "marketing_channel": "How did you hear about us?",
            "other_marketing_channel": "If you chose Other, please specify here.",
            "project_name": "Project title",
            "other_project_category": "If you chose Other, please specify here.",
            "description": "Please provide a brief description for your project, "
                           "including the problem you hope to solve or the question "
                           "you hope to answer with the help of your Discovery team.",
            "other_project_category": "If you picked Other above, describe your category below"
        }