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
            url('status_summary', status_summary, name='status_summary')
        ]
        return additional_urls + urls

# Helper
def col_name(name):
    return name.title().replace(' ', '_')

def verbose_name(name):
    if name == 'Total':
        return 'Total Applications'
    return name.title().replace('_', ' ')

col_rename = {col_name(t[0]):verbose_name(str(t[1])) for t in Application.ApplicationStatus.choices}
status = list(col_rename.keys())
total = [col_name('Total')]
group = [col_name('Student'), col_name('First_Name'), col_name('Last_Name'), col_name('Project')]
for col in total + group:
    col_rename[col] = verbose_name(col)
col_order = group + status + total
inv_sem_map = {v:k for k, v in Project.sem_mapping.items()}
filters = [(s, f'Has status: {col_rename[s]}') for s in status]

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
    filter_in_query = [f for f, _ in filters if request.GET.get(f, False) == "IN"]
    filter_out_query = [f for f, _ in filters if request.GET.get(f, False) == "OUT"]
    group_query = request.GET.get('group', 'student')
    semester_query = request.GET.get('semester', inv_sem_map[config.CURRENT_SEMESTER])
    applicant_query = request.GET.get('applicant','students')
    export_query = request.GET.get('export', None)
    page_query = request.GET.get("page", 1)

    sort_query = col_name(sort_query)
    formatted_group_query = col_name(group_query)
    formatted_applicant_query = col_name(applicant_query)

    if not filter_in_query and not filter_out_query:
        filter_in_query = [f for f, _ in filters]

    extra = []
    if formatted_group_query == col_name('Student'):
        extra = [col_name('First_Name'), col_name('Last_Name')]
    table_col = extra + [formatted_group_query] + status + [col_name('Total')]

    projs = Project.objects.filter(semester=semester_query.upper())
    filtered = Application.objects.filter(project__in=projs)

    # Data Scholar Filter
    ds = DataScholar.objects.values('email_address')
    if formatted_applicant_query == col_name('Scholars'):
        filtered = filtered.filter(student__in=ds)

    df = pd.DataFrame([model_to_dict(row) for row in filtered])

    if df.shape[0] == 0:
        table_row_list = [{c:"" for c in col_order}]
    else:
        df.columns = [col_name(t) for t in df.columns]

        for s in status:
            df[col_name(s)] = df[col_name('status')] == s.upper()
        df[col_name('Total')] = 1
        table = df.groupby(formatted_group_query).sum()
        table.reset_index(inplace=True)

        if formatted_group_query == col_name('Project'):
            table[formatted_group_query] = [Project.objects.get(id=id).project_name for id in table[formatted_group_query]]
        elif formatted_group_query ==  col_name('Student'):
            table[col_name('First_Name')] = [Student.objects.get(email_address=id).first_name for id in table[formatted_group_query]]
            table[col_name('Last_Name')] = [Student.objects.get(email_address=id).last_name for id in table[formatted_group_query]]

        table = table[table_col]

        # Status Filter
        in_indices = []
        out_indices = []
        for s in status:
            cond = [i for i, val in zip(table.index, table[s]) if val > 0]
            if s in filter_in_query:
                in_indices.extend(cond)
            elif s in filter_out_query:
                out_indices.extend(cond)
        indices = list(set(in_indices).difference(set(out_indices)))
        table = table.iloc[indices]

        table_row_list = []
        for _, row in table.iterrows():
            table_row_list.append(row.to_dict())

    table = TrackingTable(table_row_list)
    table.order_by = sort_query
    table.paginate(page=page_query, per_page=pages)
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
       applicant_support=[('students', 'Show all students'), ('scholars', 'Show only Data Scholars')],
       semester_support=[(s[0], s[1]) for s in Semester.choices],
       export_support=table.export_querys,
       # Current Filters
       filter_in_query=filter_in_query,
       filter_out_query=filter_out_query,
       group_query=group_query,
       applicant_query=applicant_query,
       semester_query=semester_query,
    )
    return TemplateResponse(request, "admin/status_summary.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
