from django.contrib import admin

from projects.models import Question

from .models import Answer, DataScholar, Student


class StudentAdmin(admin.ModelAdmin):

    list_display = ['last_name', 'first_name', 'student_id', 'email_address', ]
    ordering = list_display.copy()

admin.site.register(Student, StudentAdmin)


class DataScholarAdmin(admin.ModelAdmin):

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
