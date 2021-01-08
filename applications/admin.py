from django.contrib import admin
from .models import Application

# Register your models here.

class ApplicationAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'project', 'student', 'status')
    ordering = ('id', )

admin.site.register(Application, ApplicationAdmin)
