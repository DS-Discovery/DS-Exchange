from django.contrib.admin import AdminSite
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

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
    # ...
    context = dict(
       title='Status summary',
       has_permission=request.user.is_authenticated,
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
