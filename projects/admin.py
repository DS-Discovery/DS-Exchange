# Register your models here.
from django.contrib import admin
from django.forms import ModelForm, Textarea

from .models import Partner
from .models import Project
from .models import Question
from .models import PartnerProjectInfo


class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 3


class PartnerProjectInfoInline(admin.TabularInline):
    model = PartnerProjectInfo
    extra = 2
    ordering = ("project", )


class PartnerAdmin(admin.ModelAdmin):

    fields = [ 'email_address','first_name','last_name',]
    inlines = [PartnerProjectInfoInline]

    def all_projects(self, obj):
        return ";\n".join([str(p.project) for p in PartnerProjectInfo.objects.filter(partner = obj)])

    list_display = ['last_name', 'first_name', 'email_address']
    ordering = list_display.copy()

admin.site.register(Partner, PartnerAdmin)


class ProjectAdminForm(ModelForm):
  class Meta:
    model = Project
    widgets = {
      'description': Textarea(attrs={"cols": "100"}),
    }
    fields = '__all__'


class ProjectAdmin(admin.ModelAdmin):
    
    form =  ProjectAdminForm
    fields = ['semester', 'project_name', 'organization', 'project_category', 'student_num', 'description']
    inlines = [QuestionInLine]
    list_display = ('project_name', 'project_category', 'semester', )
    list_filter = ['project_category']
    search_fields = ['project_name']
    ordering = ("project_name", )

admin.site.register(Project, ProjectAdmin)
