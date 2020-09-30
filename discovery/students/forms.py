import datetime

from django import forms


from .models import Answer
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_text', )
