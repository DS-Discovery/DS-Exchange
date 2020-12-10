from django.contrib import admin
from .models import Application

# Register your models here.

class ApplicationAdmin(admin.ModelAdmin):
    
    list_display = ('project', 'student')

admin.site.register(Application, ApplicationAdmin)

