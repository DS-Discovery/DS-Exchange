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

class StudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        # fields = "__all__"
        fields = (
            'first_name',
            'last_name',
            'student_id',
            'college',
            'major',
            'year',
            *model.default_skills.keys(),
        )


class EditStudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = (
            'first_name',
            'last_name',
            'college',
            'major',
            'year',
            'resume_link',
            'general_question',
            *model.default_skills.keys(),
        )


class EditPartnerSignupForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = (
            'first_name',
            'last_name',
       
            )

