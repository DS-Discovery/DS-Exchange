from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from projects.models import Question

from .models import Answer, DataScholar, Student


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student


class StudentAdmin(ImportExportModelAdmin):

    resource_class = StudentResource
    list_display = ['last_name', 'first_name', 'student_id', 'email_address', ]
    ordering = list_display.copy()
    search_fields = ('email_address', 'student_id', 'first_name','last_name')

admin.site.register(Student, StudentAdmin)


class DataScholarResource(resources.ModelResource):
    class Meta:
        model = DataScholar


class DataScholarAdmin(ImportExportModelAdmin):

    resource_class = DataScholarResource
    list_display = ["email_address"]
    ordering = list_display.copy()

admin.site.register(DataScholar, DataScholarAdmin)


class AnswerAdmin(admin.ModelAdmin):

    def question_text(self, obj):
        val = [obj.question]
       
        return ";\n".join([p.question_text for p in val])

    list_display = ('application', 'question_id', 'question_text')
    readonly_fields = ['question_text',]

admin.site.register(Answer, AnswerAdmin)
