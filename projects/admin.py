import json
import logging

from django import forms
from django.contrib import admin
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy  as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from students.models import Student

from .models import get_default_skills, Partner, PartnerProjectInfo, Project, Question


logger = logging.getLogger(__name__)


class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 3


class PartnerProjectInfoInline(admin.TabularInline):
    model = PartnerProjectInfo
    extra = 2
   # ordering = ("project", )


class PartnerResource(resources.ModelResource):
    class Meta:
        model = Partner


class PartnerAdmin(ImportExportModelAdmin):

    resource_class = PartnerResource
    fields = [ 'email_address','first_name','last_name',]
    inlines = [PartnerProjectInfoInline]
    search_fields = ('email_address', 'first_name', 'last_name')

    def all_projects(self, obj):
        return ";\n".join([str(p.project) for p in PartnerProjectInfo.objects.filter(partner = obj)])

    list_display = ['last_name', 'first_name', 'email_address', 'all_projects']
    ordering = ['last_name', 'first_name', 'email_address']

admin.site.register(Partner, PartnerAdmin)


class PrettyJSONWidget(Textarea):

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs['style'] = "font-family: monospace;"
            # self.attrs['cols'] = 100
            return value
        except Exception as e:
            logger.warning("Error while formatting JSON: {}".format(e))
            return super(PrettyJSONWidget, self).format_value(value)


class ProjectAdminForm(ModelForm):
    class Meta:
        model = Project
        widgets = {
            'description': Textarea(attrs={"cols": "100"}),
            'organization_description': Textarea(attrs={"cols": "100"}),
            'timeline': Textarea(attrs={"cols": "100"}),
            'project_workflow': Textarea(attrs={"cols": "100"}),
            'dataset': Textarea(attrs={"cols": "100"}),
            'deliverable': Textarea(attrs={"cols": "100"}),
            'skillset': PrettyJSONWidget(attrs={"cols": "100"}),
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        md_help = "This field supports Markdown syntax (but please don't use Markdown headers)."
        for f in ["description", "timeline", "project_workflow"]:
            self.fields[f].help_text = md_help
        self.fields["project_category"].help_text = "Please enter as a semicolon-delimited string, e.g. <code style='font-size: inherit;'>Academic;Government</code>."
        self.fields["skillset"].help_text = f"The values in the JSON object above should be among the keys in this mapping: <code style='font-size: inherit;'>{Student.skill_levels_options}</code>."
        
        # for s, l in self.instance.skillset.items():
        #     # self.fields[s] = forms.ChoiceField(choices=Student.skill_levels, label=_(s), widget=forms.Select())
        #     self.fields[s] = forms.CharField()
        #     self.fields[s].initial = self.instance.skillset[s]


class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project




class ApprovedProjectAdmin(ImportExportModelAdmin):
    
    resource_class = ProjectResource
    form = ProjectAdminForm
    # fields = ['semester', 'project_name', 'organization', 'project_category', 'student_num', 'description']
    inlines = [QuestionInLine]
    def all_partners(self, obj):
        return ";\n".join([str(p.partner) for p in PartnerProjectInfo.objects.filter(project = obj)])
    list_display = ('project_name', 'project_category', 'semester', 'num_applications', 'all_partners')
    list_filter = ['project_category']
    search_fields = ['project_name']
    ordering = ("project_name", )
    actions = ['unapprove_selected']
    
    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)


    def get_queryset(self, request):
        return self.model.objects.filter(is_approved = True)

class PendingProjectAdmin(ImportExportModelAdmin):
    
    resource_class = ProjectResource
    form = ProjectAdminForm
    # fields = ['semester', 'project_name', 'organization', 'project_category', 'student_num', 'description']
    inlines = [QuestionInLine]
    def all_partners(self, obj):
        return ";\n".join([str(p.partner) for p in PartnerProjectInfo.objects.filter(project = obj)])
    list_display = ('project_name', 'project_category', 'semester', 'num_applications', 'all_partners')
    list_filter = ['project_category']
    search_fields = ['project_name']
    ordering = ("project_name", )
    actions = ['approve_selected']
    
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)

    def get_queryset(self, request):
        return self.model.objects.filter(is_approved = False)

class PendingProject(Project):
    class Meta:
        proxy = True
admin.site.register(PendingProject, PendingProjectAdmin)
admin.site.register(Project, ApprovedProjectAdmin)
