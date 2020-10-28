
from django.db import models
from students.models import Student
from projects.models import Partner
from django.contrib.auth.models import User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email
        def find_usertype(email_address):
            query = Partner.objects.filter(email_address=email_address)
            print("PARTNER EMAIL QUERY" + query)
            if len(query) > 0:
                
                group = Group.objects.get(name='Partner')
                return group
            group = Group.objects.get(name='Student')
            return group
    
    
        # user.groups.add(find_usertype(user.email))



        return user


# class StudentUser(models.Model):
#     student = models.ForeignKey('students.Student', on_delete=models.CASCADE)

# class PartnerUser(models.Model):
#     partner = models.ForeignKey('projects.Partner', on_delete=models.CASCADE)




