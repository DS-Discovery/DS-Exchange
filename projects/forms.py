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
            )