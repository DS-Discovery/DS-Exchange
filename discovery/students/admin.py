from django.contrib import admin

from .models import Student
from .models import Answer
# from .models import Question
class StudentAdmin(admin.ModelAdmin):

    list_display = ('email_address', 'first_name', 'last_name')




admin.site.register(Student, StudentAdmin)

class AnswerAdmin(admin.ModelAdmin):

    list_display = ('student', 'question')
    # list_display = ('email_address', 'question')




admin.site.register(Answer, AnswerAdmin)


# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('question_text', 'partner')
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Question)
