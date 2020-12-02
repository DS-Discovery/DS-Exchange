# Register your models here.
from django.contrib import admin

from .models import Partner
from .models import Project
from .models import Question




class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 3



class PartnerAdmin(admin.ModelAdmin):

    fields = [ 'email_address','first_name','last_name', 'projects',]
    
    def all_projects(self, obj):
        return "\n".join([p.project_name for p in obj.projects.all()])
    # search_fields =['projects',]
    list_display = ['email_address', 'all_projects', ]


admin.site.register(Partner, PartnerAdmin)

class ProjectAdmin(admin.ModelAdmin):
    
    fields = ['semester', 'year', 'project_name', 'organization', 'project_category', 'student_num', 'description']
    inlines = [QuestionInLine]
    list_display = ('project_name', 'project_category', 'semester', 'year')
    list_filter = ['project_category']
    search_fields = ['project_name']


admin.site.register(Project, ProjectAdmin)
