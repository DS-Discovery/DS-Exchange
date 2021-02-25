from django.contrib.admin import AdminSite
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

from applications.models import Application
from projects.models import Semester, Project
from students.models import Student, DataScholar

from django.forms import model_to_dict
import pandas as pd
import django_tables2 as tables

# Helper
def col_name(name):
    return name.title()

col_rename = {col_name(t[0]):col_name(str(t[1])) for t in Application.ApplicationStatus.choices}
status = list(col_rename.keys())
total = [col_name('Total')]
group = [col_name('Student'), col_name('First_Name'), col_name('Last_Name'), col_name('Project')]
for col in total + group:
    col_rename[col] = col_name(col).replace('_', ' ')
col_order = group + status + total

class TrackingTable(tables.Table):
    for column in col_order:
        if column in status:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{col_rename[column]}")'
        else:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{col_rename[column]}")'
        exec(cmd)

class DiscoveryAdmin(AdminSite):
    def get_urls(self):
        urls = super(DiscoveryAdmin, self).get_urls()
        additional_urls = [
            url(r'status_summary/', status_summary),
        ]
        return additional_urls + urls


# Custom Views
@staff_member_required
def status_summary(request):
    sort_col = request.GET.get('sort', 'total')
    filter = request.GET.get('filter', 'all')
    group_col = request.GET.get('group', 'student')
    sem_col = request.GET.get('semester', 'SP21')

    sort_col = col_name(sort_col)
    group_col = col_name(group_col)

    extra = []
    if group_col ==  col_name('Student'):
        extra = ['First_Name', 'Last_Name']
    col = col_name(group_col)
    col_list = extra + [col] + status + [col_name('Total')]

    projs = Project.objects.filter(semester=sem_col)
    filtered = Application.objects.filter(project__in=projs)

    if filter == 'data_scholars':
        ds = DataScholar.objects.values('email_address')
        filtered = filtered.filter(student__in=ds)

    df = pd.DataFrame([model_to_dict(row) for row in filtered])

    if df.shape[0] == 0:
        table_row_list = [{c:"" for c in col_order}]
    else:
        df.columns = [col_name(t) for t in df.columns]

        for s in status:
            df[col_name(s)] = df[col_name('status')] == s.upper()
        df[col_name('Total')] = 1
        table = df.groupby(group_col).sum()

        table.reset_index(inplace=True)

        if group_col == col_name('Project'):
            table[group_col] = [Project.objects.get(id=id).project_name for id in table[group_col]]
        elif group_col ==  col_name('Student'):
            table[col_name('First_Name')] = [Student.objects.get(email_address=id).first_name for id in table[group_col]]
            table[col_name('Last_Name')] = [Student.objects.get(email_address=id).last_name for id in table[group_col]]

        table = table[col_list]

        table_row_list = []
        for _, row in table.iterrows():
            table_row_list.append(row.to_dict())

    table = TrackingTable(table_row_list)
    table.order_by = sort_col
    table.paginate(page=request.GET.get("page", 1), per_page=10)

    table.exclude = set(group).difference(col_list)

    context = dict(
       title='Status summary',
       has_permission=request.user.is_authenticated,
       site_url=True,
       table=table,
       semester=Semester,
       filter=filter,
       group_col=group_col,
       sem_col=sem_col,
    )
    return TemplateResponse(request, "admin/status_summary.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
