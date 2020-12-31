import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm, Textarea, TextInput, ChoiceField
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

from students.models import Student
from projects.models import Partner, Project


class StudentSignupForm(forms.ModelForm):
    # skills = JSONField()

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
            'general_question',
            # *model.default_skills.keys(),
        )

        labels = {
            'general_question': _('Why are you interested in the Discovery program? What do you hope to gain?'),
        }
        widgets = {
            'general_question': Textarea(attrs={'class': 'form-control'})
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for s, l in self.instance.skills.items():
            self.fields[s] = ChoiceField(choices=Student.skill_levels)
            self.fields[s].initial = self.instance.skills[s]


class EditStudentSignupForm(forms.ModelForm):
    # skills = JSONField()

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
            'general_question', 
            # *model.default_skills.keys(),
        )

        labels = {
            'general_question': _('Why are you interested in the Discovery program? What do you hope to gain?'),
        }

        widgets = {
            'general_question': Textarea(attrs={'class': 'form-control'})
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for s, l in self.instance.skills.items():
            self.fields[s] = ChoiceField(choices=Student.skill_levels)
            self.fields[s].initial = self.instance.skills[s]


class EditPartnerSignupForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = (
            'first_name',
            'last_name',
       
            )

