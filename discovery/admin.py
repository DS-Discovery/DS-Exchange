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
from constance import config
from django_tables2.export.views import ExportMixin
from django_tables2.export.export import TableExport
from django_tables2.paginators import LazyPaginator

class DiscoveryAdmin(AdminSite):
    def get_urls(self):
        urls = super(DiscoveryAdmin, self).get_urls()
        additional_urls = [
            url(r'status_summary/', status_summary),
        ]
        return additional_urls + urls

# Helper
def col_name(name):
    return name.title().replace(' ', '_')

def verbose_name(name):
    return name.title().replace('_', ' ')

col_rename = {col_name(t[0]):verbose_name(str(t[1])) for t in Application.ApplicationStatus.choices}
status = list(col_rename.keys())
total = [col_name('Total')]
group = [col_name('Student'), col_name('First_Name'), col_name('Last_Name'), col_name('Project')]
for col in total + group:
    col_rename[col] = verbose_name(col)
col_order = group + status + total
inv_sem_map = {v:k for k, v in Project.sem_mapping.items()}
filters = [('data_scholar', 'Is Data Scholars')] + [(s, f'Has status: {col_rename[s]}') for s in status]

class TrackingTable(ExportMixin, tables.Table):
    export_querys = ['csv', 'json', 'latex', 'ods', 'tsv', 'xls', 'xlsx', 'yaml']
    for column in col_order:
        if column in status:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{col_rename[column]}")'
        else:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{col_rename[column]}")'
        exec(cmd)
    paginator_class = LazyPaginator

# Custom Views
@staff_member_required
def status_summary(request, pages=10):
    sort_query = request.GET.get('sort', 'total')
    filter_query = [f for f, _ in filters if bool(request.GET.get(f, False))]
    group_query = request.GET.get('group', 'student')
    semester_query = request.GET.get('semester', inv_sem_map[config.CURRENT_SEMESTER])
    export_query = request.GET.get('export', None)
    page_query = request.GET.get("page", 1)

    sort_query = col_name(sort_query)
    group_query = col_name(group_query)

    extra = []
    if group_query == col_name('Student'):
        extra = [col_name('First_Name'), col_name('Last_Name')]
    col = col_name(group_query)
    table_col = extra + [col] + status + [col_name('Total')]

    projs = Project.objects.filter(semester=semester_query.upper())
    filtered = Application.objects.filter(project__in=projs)

    # Data Scholar Filter
    if 'data_scholar' in filter_query:
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
        table = df.groupby(group_query).sum()
        table.reset_index(inplace=True)

        if group_query == col_name('Project'):
            table[group_query] = [Project.objects.get(id=id).project_name for id in table[group_query]]
        elif group_query ==  col_name('Student'):
            table[col_name('First_Name')] = [Student.objects.get(email_address=id).first_name for id in table[group_query]]
            table[col_name('Last_Name')] = [Student.objects.get(email_address=id).last_name for id in table[group_query]]

        table = table[table_col]

        # Status Filter
        for s in status:
            if s in filter_query:
                table = table[[i > 0 for i in table[s]]]

        table_row_list = []
        for _, row in table.iterrows():
            table_row_list.append(row.to_dict())

    table = TrackingTable(table_row_list)
    table.paginate(page=page_query, per_page=pages)
    table.order_by = sort_query
    # Hide columns not used by the table
    table.exclude = set(col_order).difference(table_col)

    # To export filtered table
    if TableExport.is_valid_format(export_query):
        exporter = TableExport(export_query, table)
        return exporter.response('status_tracking.{}'.format(export_query))
        
    context = dict(
       title='Status summary',
       has_permission=request.user.is_authenticated,
       site_url=True,
       table=table,
       # Allowable Values
       filter_support=filters,
       group_support=[('student', 'students'), ('project', 'projects')],
       semester_support=[(s[0], s[1]) for s in Semester.choices],
       export_support=table.export_querys,
       # Current Filters
       filter_query=filter_query,
       group_query=group_query,
       semester_query=semester_query,
    )
    return TemplateResponse(request, "admin/status_summary.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
