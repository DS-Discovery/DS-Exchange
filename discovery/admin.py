from django.contrib.admin import AdminSite
from django.urls import re_path as url
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

from applications.models import Application
from projects.models import Semester, Project, PartnerProjectInfo
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
            url('status_summary', status_summary, name='status_summary'),
            url('project_roster', project_roster, name='project_roster')
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
application_status_mapping = {t[0]:t[1] for t in Application.ApplicationStatus.choices}
status = list(col_rename.keys())
total = [col_name('Total')]
student_group = [col_name('Student'), col_name('First_Name'), col_name('Last_Name')]
project_group = [col_name('Project'), col_name('Contact')]
group = student_group + project_group
for col in total + group:
    col_rename[col] = verbose_name(col)
col_order = group + status + total
inv_sem_map = {v:k for k, v in Project.sem_mapping.items()}
filters = [(s, f'{col_rename[s]}') for s in status]

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
    group_query = request.GET.get('group', 'student')
    semester_query = request.GET.get('semester', inv_sem_map[config.CURRENT_SEMESTER])
    applicant_query = request.GET.get('applicant','students')
    export_query = request.GET.get('export', None)
    page_query = request.GET.get("page", 1)
    any_all_query = request.GET.get("any_all", "ANY")
    filter_query = [f for f, _ in filters if request.GET.get(f, False) == "True"]

    sort_query = col_name(sort_query)
    formatted_group_query = col_name(group_query)
    formatted_applicant_query = col_name(applicant_query)

    extra = []
    if formatted_group_query == col_name('Student'):
        extra = student_group
    if formatted_group_query == col_name('Project'):
        extra = project_group
    table_col = extra + status + [col_name('Total')]

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
            table[col_name('Contact')] = [", ".join([ppi.partner.email_address for ppi in PartnerProjectInfo.objects.filter(project=Project.objects.get(id=id))]) for id in table[formatted_group_query]]
            table[formatted_group_query] = [Project.objects.get(id=id).project_name for id in table[formatted_group_query]]
        elif formatted_group_query ==  col_name('Student'):
            table[col_name('First_Name')] = [Student.objects.get(email_address=id).first_name for id in table[formatted_group_query]]
            table[col_name('Last_Name')] = [Student.objects.get(email_address=id).last_name for id in table[formatted_group_query]]

        table = table[table_col]

        # Status Filter
        if any_all_query == "ALL":
            filter_threshold = len(filter_query)
        if any_all_query == "ANY":
            filter_threshold = 1
        indices = [i for i, val in table.iterrows() if sum([val[s] > 0 for s in filter_query]) >= filter_threshold]
        table = table.iloc[indices] 

        table_row_list = []
        for _, row in table.iterrows():
            table_row_list.append(row.to_dict())
        if len(table_row_list) == 0:
            table_row_list = [{c:"" for c in col_order}]

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
       any_all_support=[('ANY', 'ANY'), ('ALL', 'ALL')],
       semester_support=[(s[0], s[1]) for s in Semester.choices],
       export_support=table.export_querys,
       # Current Filters
       filter_query=filter_query,
       group_query=group_query,
       applicant_query=applicant_query,
       semester_query=semester_query,
       any_all_query=any_all_query,
    )
    return TemplateResponse(request, "admin/status_summary.html", context)


class RosterTable(ExportMixin, tables.Table):
    export_querys = ['csv', 'json', 'latex', 'ods', 'tsv', 'xls', 'xlsx', 'yaml']
    col_order = [col_name('Email_Address'), col_name('First_Name'), col_name('Last_Name'), col_name('Status')]
    for column in col_order:
        if column in status:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{column}")'
        else:
            cmd = f'{column} = tables.Column(orderable=True, verbose_name="{column}")'
        exec(cmd)
    paginator_class = LazyPaginator

@staff_member_required
def project_roster(request, pages=10):
   
    semester_query = request.GET.get('semester', inv_sem_map[config.CURRENT_SEMESTER])
    
    export_query = request.GET.get('export', None)
    page_query = request.GET.get("page", 1)

    projs = Project.objects.filter(semester=semester_query.upper())
    project_name_space_map = {k.project_name.replace(" ", "") : k.project_name for k in projs}
    if len(projs) == 0:
        return "No projs"
    proj_query = request.GET.get('project', projs[0].project_name.replace(" ", ""))
    proj = Project.objects.filter(project_name=project_name_space_map[proj_query])[0]
    filtered = Application.objects.filter(project=proj)
    students_emails = filtered.values_list("student")

    
    students = Student.objects.filter(email_address__in = students_emails)

    df = pd.DataFrame([model_to_dict(s) for s in students])
    if df.shape[0] == 0:
        table_row_list = [{c:"" for c in col_order}]
    else:

        df['Status'] = [application_status_mapping[Application.objects.get(student=e).status] for e in df['email_address']]
        df.columns = [col_name(t) for t in df.columns]
        
        table = df
        table_row_list = []
        for _, row in table.iterrows():
            table_row_list.append(row.to_dict())
        if len(table_row_list) == 0:
            table_row_list = [{c:"" for c in col_order}]
  
    table = RosterTable(table_row_list)
    table.paginate(page=page_query, per_page=pages)

    # To export filtered table
    if TableExport.is_valid_format(export_query):
        exporter = TableExport(export_query, table)
        return exporter.response('project_roster.{}'.format(export_query))
    possible_semesters = set([s['semester'] for s in Project.objects.order_by().values('semester').distinct()])
    context = dict(
       title='Project Roster for {}'.format(proj_query),
       has_permission=request.user.is_authenticated,
       site_url=True,
       table=table,
       # Allowable Values
       filter_support=filters,
       semester_support=[(s[0], s[1]) for s in Semester.choices if s[0] in possible_semesters],
       proj_support = [(p.project_name.replace(" ", ''),p.project_name)  for p in projs],
       export_support=table.export_querys,
       semester_query=semester_query,
       proj_query = proj_query,
    )
    return TemplateResponse(request, "admin/project_roster.html", context)

admin_site = DiscoveryAdmin(name='discovery_admin')
