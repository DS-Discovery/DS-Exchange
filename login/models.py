
from django.db import models
from students.models import Student
from projects.models import Partner
from django.contrib.auth.models import User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Group
from allauth.socialaccount.signals import pre_social_login
from allauth.account.utils import perform_login
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from django.contrib.auth.management import create_permissions


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email

        def populateGroup(self, user):
            pass

        return user




@receiver(user_signed_up)
def populateGroup(sender, user, **kwargs):
        user = User.objects.get(email=user.email)
  
        query = Partner.objects.filter(email_address=user.email)


        Group.objects.get_or_create(name='Partner')
        Group.objects.get_or_create(name='Student')
        
        if len(query) > 0:
            partner = Group.objects.get(name = 'Partner')
            user.groups.add(partner)
        else:
            student = Group.objects.get(name = 'Student')
            user.groups.add(student)
        user.save()





