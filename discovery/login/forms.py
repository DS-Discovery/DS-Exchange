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
from django.forms import ModelForm, Textarea, TextInput
class StudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        # fields = "__all__"
        # general_question = forms.CharField(label = "Why are you interested in the Discovery program? What do you hope to gain?")
        fields = (
            'first_name',
            'last_name',
            'student_id',
            'college',
            'major',
            'year',
            'resume_link',
            'general_question'
            )
        labels = {
            'general_question': _('Why are you interested in the Discovery program? What do you hope to gain?'),
        }
        widgets = {
            'general_question': Textarea(attrs={'class': 'form-control'})
            }


class EditStudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        # general_question = forms.CharField(label = "Why are you interested in the Discovery program? What do you hope to gain?")
        fields = (
            'first_name',
            'last_name',
            'college',
            'major',
            'year',
            'resume_link',
            'general_question'
        )
        labels = {
            'general_question': _('Why are you interested in the Discovery program? What do you hope to gain?'),
        }

        widgets = {
            'general_question': Textarea(attrs={'class': 'form-control'})
            }
class EditPartnerSignupForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = (
            'first_name',
            'last_name',
       
            )

