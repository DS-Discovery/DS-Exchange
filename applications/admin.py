from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Application


class ApplicationResource(resources.ModelResource):
    class Meta:
        model = Application


class ApplicationAdmin(ImportExportModelAdmin):

    resource_class = ApplicationResource
    list_display = ('id', 'project', 'student', 'status')
    ordering = ('id', )

admin.site.register(Application, ApplicationAdmin)
