from allauth.account.forms import LoginForm
import datetime

from django import forms

from allauth.socialaccount.forms import SignupForm

# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from students.models import Student
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
# from login.models import StudentUser, User
from django.db import transaction

# class StudentProfileForm(forms.ModelForm):
#     first_name = forms.CharField(label=_(u''), max_length=30)
#     last_name = forms.CharField(label=_(u''), max_length=30)
#     full_name = forms.CharField(label=_(u''), max_length=30)
#     student_id = forms.CharField(label=_(u''), max_length=30)
#     college = forms.CharField(label=_(u''), max_length=30)
#     major = forms.CharField(label=_(u''), max_length=30)
#     year = forms.CharField(label=_(u''), max_length=30)


#     # fields = ("email_address", )
    
#     class Meta:
#         model = Student
#         fields = '__all__'
#     @transaction.atomic # ensure operations are done in a single database transaction and avoid data inconsistencies in case of error
#     def save(self):
#         student = super().save(commit=False)

#         student.save()

#         student = Student.objects.create(email_address = email_address)

#         # student = student.email_address = 
#         # studentuser.student.email_address.add(*self.cleaned_data.get('email_address'))
#         return student

#     # def save(self, *args, **kw):
#     #     super(StudentProfileForm, self).save(*args, **kw)
#     #     self.instance.user.first_name = self.cleaned_data.get('first_name')
#     #     self.instance.user.last_name = self.cleaned_data.get('last_name')
#     #     self.instance.user.save()

#     # class Meta:
#     #     model = Student

# class EditStudentProfileForm(forms.ModelForm):
#     fields = ("full_name", )


# class PartnerProfileForm(forms.ModelForm):
#     first_name = forms.CharField(label=_(u''), max_length=30)
#     last_name = forms.CharField(label=_(u''), max_length=30)
#     email_address = forms.CharField(label=_(u''), max_length=30)
#     # fields = ("email_address", )
    
#     class Meta:
#         model = Student
#         fields = '__all__'
#     @transaction.atomic
#     def save(self):
#         user = super().save(commit=False)
#         user.is_student = True
#         user.save()
#         studentuser = StudentUser.objects.create(user = user)
#         student = Student.objects.create(email_address = email_address)
#         studentuser.student = student

#         return user


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
    # first_name = forms.CharField(label=_(u'First Name'), max_length=30)
    # last_name = forms.CharField(label=_(u'Last Name'), max_length=30)
    # # full_name = forms.CharField(label=_(u'Full Name'), max_length=30)
    # student_id = forms.CharField(label=_(u'Student ID'), max_length=30)
    # college = forms.CharField(label=_(u'College'), max_length=30)
    # major = forms.CharField(label=_(u'Major'), max_length=30)
    # year = forms.CharField(label=_(u'Year'), max_length=30)

    # # Override the save method to save the extra fields
    # # (otherwise the form will save the User instance only)
    # def save(self, request):
    #     # Save the User instance and get a reference to it
    #     user = super(StudentSignupForm, self).save(request)

    #     student = Student.objects.create(email_address = self.cleaned_data.get('email_address'), 
    #                                         full_name = self.cleaned_data.get('full_name'), 
    #                                         student_id = self.cleaned_data.get('student_id'), 
    #                                         college = self.cleaned_data.get('college'), 
    #                                         major = self.cleaned_data.get('major'), 
    #                                         year = self.cleaned_data.get('year'))
    #     # student_user = StudentUser(
    #     #     user=user,
    #     #     student = student
    #     # )
    #     student.save()

    #     # Remember to return the User instance (not your custom user,
    #     # the Django one), otherwise you will get an error when the
    #     # complete_signup method will try to look at it.
    #     return student.student.full_name

# class StudentUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         # fields = ('email_address', 'full_name', 'student_id', 'college', 'major', 'year')
#         fields = ('user', 'student')

class EditStudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = (
            'full_name',
            'college',
            'major',
            'year',
        )