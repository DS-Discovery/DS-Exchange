from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_text', 'question_num')
