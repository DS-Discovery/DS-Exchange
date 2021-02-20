from django.contrib.admin import AdminSite
from django.conf.urls import url
from django.template.response import TemplateResponse

class DiscoveryAdmin(AdminSite):
    def get_urls(self):
        urls = super(DiscoveryAdmin, self).get_urls()
        additional_urls = [
            url(r'status_summary/', self.status_summary),
            url(r'overview/', self.overview),
        ]
        return additional_urls + urls

    # Custom Views
    def status_summary(self, request):
        # ...
        context = dict(
           title='Status summary'
        )
        return TemplateResponse(request, "admin/status_summary.html", context)

    def overview(self, request):
        # ...
        context = dict(
           key='value',
        )
        return TemplateResponse(request, "admin/overview.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
