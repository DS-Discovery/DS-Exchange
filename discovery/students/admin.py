from django.contrib import admin

from .models import Student
from .models import Question
admin.site.register(Student)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'partner')
admin.site.register(Question, QuestionAdmin)
# admin.site.register(Question)
