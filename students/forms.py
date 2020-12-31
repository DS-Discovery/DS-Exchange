from django import forms
from django.utils.translation import ugettext_lazy as _

from projects.models import Question

from .models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_text', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["question"] = forms.ModelChoiceField(Question.objects.all())
