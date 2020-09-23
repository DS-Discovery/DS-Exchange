import datetime

from django import forms
from .models import Student
from .models import Question
from .models import Answer
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class studentForm(forms.Form):
    first_name = forms.CharField(help_text= "")
    last_name = forms.CharField(help_text= "")
    def clean_renewal_date(self):
        data = self.cleaned_data['first_name']

        return data


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_text', )
