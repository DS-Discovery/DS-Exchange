import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

from students.models import Student
from projects.models import Partner, Project, PartnerNewProj

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


class PartnerProjCreation(forms.ModelForm):

    class Meta:
        model = PartnerNewProj
        fields = (
            'email',
            'first_name',
            'last_name',
            'organization_name',
            'organization_description',
            'organization_website',
            'how_did_you_hear_about_us',
            )