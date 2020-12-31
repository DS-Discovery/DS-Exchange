from django.contrib import admin

from .models import Student
from .models import Answer
from projects.models import Question
# from .models import Question
class StudentAdmin(admin.ModelAdmin):

    list_display = ('email_address', 'first_name', 'last_name')




admin.site.register(Student, StudentAdmin)




class AnswerAdmin(admin.ModelAdmin):

    def question_text(self, obj):
        # val = Question.objects.filter(project = obj.application.project, question = obj.question)
        val = [obj.question]
       
        return ";\n".join([p.question_text for p in val])

    list_display = ('application', 'question_id', 'question_text')
    readonly_fields = ['question_text',]

    # list_display = ('email_address', 'question')
  




admin.site.register(Answer, AnswerAdmin)


# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('question_text', 'partner')
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Question)
