from allauth.account.forms import LoginForm
import datetime

from django import forms

from allauth.socialaccount.forms import SignupForm


from students.models import Student
from projects.models import Partner
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.db import transaction

class StudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        # fields = "__all__"
        fields = (
            'full_name',
            'student_id',
            'college',
            'major',
            'year',
            )


class EditStudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = (
            'full_name',
            'college',
            'major',
            'year',
        )

# class PartnerSignupForm(forms.ModelForm):

#     class Meta:
#         model = Partner
#         # fields = "__all__"
#         fields = (
#             'email_address',
#             'first_name',
#             'last_name',
#             'organization',
#             'project_name',
#             'project_category',
#             'student_num',
#             'description',            
#             )

class EditPartnerSignupForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = (
            'first_name',
            'last_name',
            'organization',
            'project_name',
            'project_category',
            'student_num',
            'description',            
            )