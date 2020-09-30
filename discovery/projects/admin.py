# Register your models here.
from django.contrib import admin

from .models import Partner
from .models import Question



class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 3


class PartnerAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,               {'fields': ['project_name']}),
    #     ('Date information', {'fields': ['organization', 'project_category', 'email_address', 'first_name', 'last_name', 'student_num', 'description'], 'classes': ['collapse']}),
    # ]
    fields = ['project_name', 'organization', 'project_category', 'email_address','first_name','last_name','student_num', 'description']
    inlines = [QuestionInLine]
    list_display = ('project_name', 'project_category')
    list_filter = ['project_category']
    search_fields = ['project_name']



admin.site.register(Partner, PartnerAdmin)
# admin.site.register(Partner)
