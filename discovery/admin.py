from django.contrib.admin import AdminSite
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

from applications.models import Answer, Application
from projects.models import Partner, Project
from students.models import Student

from django.forms import model_to_dict
import pandas as pd

class DiscoveryAdmin(AdminSite):
    def get_urls(self):
        urls = super(DiscoveryAdmin, self).get_urls()
        additional_urls = [
            url(r'status_summary/', status_summary),
            url(r'overview/', overview),
        ]
        return additional_urls + urls

# Helper
def col_name(name, asc, sort_col, filter, group):
    o = '-' + name
    dir = 'asc'
    if name == sort_col:
        if not asc:
            o = o[1:]
            dir = 'desc'
    return f'<a class="{dir}" href="?filter={filter}&group={group}&o={o}">{name.title()}</a>'


# Custom Views
@staff_member_required
def status_summary(request):
    sort_col = request.GET.get('o', 'total')
    filter = request.GET.get('filter', 'all')
    group = request.GET.get('group', 'student')

    if sort_col[0]  == '-':
        asc = False
        sort_col = sort_col[1:]
    else:
        asc = True

    status_rename = {t[0]:col_name(str(t[1]), asc, sort_col, filter, group) for t in Application.ApplicationStatus.choices}
    df = pd.DataFrame([model_to_dict(row) for row in Application.objects.all()])
    print(df.columns)
    for status in status_rename.keys():
        df[status] = df['status'] == status
    total = col_name('total', asc, sort_col, filter, group)
    df[total] = 1
    table = df.groupby(group).sum()

    col = col_name(group, asc, sort_col, filter, group)
    table[col] = table.index
    table = table[[col] + list(status_rename.keys()) + [total]]
    table.rename(columns=status_rename, inplace=True)
    table = table.sort_values(by=col_name(sort_col, asc, sort_col, filter, group), ascending=asc)

    context = dict(
       title='Status summary',
       has_permission=request.user.is_authenticated,
       table=table.to_html(index=False, escape=False, border=0),
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
