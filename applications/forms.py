import datetime

from django import forms


from .models import Application
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('student', 'project')
