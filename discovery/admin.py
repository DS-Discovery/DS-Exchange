from django.contrib.admin import AdminSite
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

from applications.models import Answer, Application
from projects.models import Partner, Project
from students.models import Student

import django_tables2 as tables

class ApplicationTable(tables.Table):
    class Meta:
        model = Application

class DiscoveryAdmin(AdminSite):
    def get_urls(self):
        urls = super(DiscoveryAdmin, self).get_urls()
        additional_urls = [
            url(r'status_summary/', status_summary),
            url(r'overview/', overview),
        ]
        return additional_urls + urls

# Custom Views
@staff_member_required
def status_summary(request):
    order_by = request.GET.get('sort', 'status')
    table = ApplicationTable(Application.objects.all().order_by(order_by))
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    context = dict(
       title='Status summary',
       has_permission=request.user.is_authenticated,
       table=table,
    )
    return TemplateResponse(request, "admin/status_summary.html", context)

@staff_member_required
def overview(request):
    # ...
    context = dict(
       title='Overview',
       has_permission=request.user.is_authenticated,
    )
    return TemplateResponse(request, "admin/overview.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
