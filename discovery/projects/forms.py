from allauth.account.forms import LoginForm
import datetime

from django import forms

from allauth.socialaccount.forms import SignupForm


from students.models import Student
from projects.models import Partner
from projects.models import Project
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.db import transaction
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