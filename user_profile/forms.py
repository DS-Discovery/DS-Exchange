import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import CharField, ChoiceField, ModelForm, Select, Textarea, TextInput
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

from students.models import Student
from projects.models import Partner, Project


class EditStudentSignupForm(forms.ModelForm):
    # skills = JSONField()

    class Meta:
        model = Student
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
            # 'additional_skills': _("Please list any additional technical competencies that you think could be relevant."),
            'year': _('Expected Graduation Term:'),
            'first_name': 'First Name:',
            'last_name': 'Last Name:',
            'student_id': 'Student ID:',
            # 'resume_link': 'Please provide a link to your resume.',
        }

        widgets = {
            'general_question': Textarea(attrs={'class': 'form-control'}),
            # 'additional_skills': Textarea(attrs={'class': 'form-control'}),
        }

    resume_link = forms.URLField(label="Please provide a sharable link to your resume (i.e. Google Drive).")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for s, l in self.instance.skills.items():
            self.fields[s] = ChoiceField(choices=Student.skill_levels, label=_(s), widget=Select(attrs={'class': 'skill-dropdown'}))
            self.fields[s].initial = self.instance.skills[s]
        self.fields["additional_skills"] = CharField(
            max_length=1000, widget=Textarea(attrs={'class': 'form-control'}), 
            label=_("Please list any additional technical competencies that you think could be relevant.")
        )
        self.fields["additional_skills"].initial = self.instance.additional_skills
        # self.labels["additional_skills"] = 


# class EditPartnerSignupForm(forms.ModelForm):

#     class Meta:
#         model = Partner
#         fields = (
#             'first_name',
#             'last_name',
#         )

