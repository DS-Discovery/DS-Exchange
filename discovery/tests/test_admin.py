from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib.messages import get_messages

from factory_djoy import UserFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.project import ProjectFactory

from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory
from students.tests.factories.datascholar import DataScholarFactory
from applications.tests.factories.application import ApplicationFactory
from discovery.admin import admin_site
from constance import config
from projects.models import Semester
import django_tables2 as tables

import random
from collections import Counter

class AdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory()

        cls.project = ProjectFactory()

        #default student
        cls.groupTypes = ['student', 'project']
        #default current Semester (config.CURRENT_SEMESTER)
        cls.semesters = [s[0] for s in Semester.choices]
        cls.semesterCt = len(cls.semesters)
        #default ALL IN
        cls.filters = ['Sub','Rni','Int','Rwi','Ofs','Ofr','Ofa']
        cls.filterTypes = ['ANY', 'ALL']
        #default 'students'
        cls.applicantTypes = ['students', 'scholars']
        cls.default_link_values = '&any_all=ANY&Sub=True&Rni=True&Int=True&Rwi=True&Ofs=True&Ofr=True&Ofa=True'

    ### START HELPER FUNCTIONS ###

    def response_validation(self, response, groupType, semester, applicant, appList, filterArrayDict=None):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("title"), "Status summary")
        self.assertEqual(response.context.get("semester_query"), semester)
        self.assertEqual(response.context.get("group_query"), groupType)

        if not filterArrayDict == None:
            self.assertEqual(response.context.get("filter_in_query").sort(), filterArrayDict['IN'].sort())
            self.assertEqual(response.context.get("filter_out_query").sort(), filterArrayDict['OUT'].sort())

            selectedFilterSet = []
            for i in filterArrayDict['IN']:
                selectedFilterSet.append(i)

            if len(selectedFilterSet) == 0:
                selectedFilterSet = self.filters.copy()

            for i in filterArrayDict['OUT']:
                if i in selectedFilterSet:
                    selectedFilterSet.remove(i)
        else:
            selectedFilterSet = self.filters.copy()

        selectedFilterSet = [x.upper() for x in selectedFilterSet]

        table = response.context.get("table")

        qualifiedAppList = []
        qualifiedSet = set()
        # compute the expected Total rows
        for j in appList:
            if j.project.semester == semester and j.status in selectedFilterSet:
                if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                    qualifiedAppList.append(j)

        if len(qualifiedAppList) > 0:
            if groupType == 'student':
                for j in qualifiedAppList:
                    qualifiedSet.add(j.student.email_address)

                # Return only applied student
                for i in table.paginated_rows.data:
                    self.assertIn(i['Student'], qualifiedSet)
                    statusList= []
                    expectedRowCt = 0
                    for j in appList:
                        if j.student.email_address == i['Student'] and j.project.semester == semester:
                            if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                                expectedRowCt = expectedRowCt + 1
                                statusList.append(j.status)

                    if expectedRowCt > 0:
                        self.assertEqual(i['Total'], expectedRowCt)
                        for k in self.filters:
                            self.assertEqual(i[k], statusList.count(k.upper()))
            else:
                for j in qualifiedAppList:
                    qualifiedSet.add(j.project.project_name)

                for i in table.paginated_rows.data:
                    self.assertIn(i['Project'], qualifiedSet)
                    statusList = []
                    expectedRowCt = 0
                    for j in appList:
                        if j.project.project_name == i['Project'] and j.project.semester == semester:
                            if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                                expectedRowCt = expectedRowCt + 1
                                statusList.append(j.status)

                    if expectedRowCt > 0:
                        self.assertEqual(i['Total'], expectedRowCt)
                        for k in self.filters:
                            self.assertEqual(i[k], statusList.count(k.upper()))

            self.assertEqual(len(table.paginated_rows.data), len(qualifiedSet))

    ### END HELPER FUNCTIONS ###

    def test_access_status_summary_not_logged_in(self):
        response = self.client.get(reverse('admin:status_summary'))
        redirect_url = f'/admin/login/?next=/admin/status_summary'
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_access_status_summary_student_logged_in(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        redirect_url = f'/admin/login/?next=/admin/status_summary'
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_access_status_summary_user_logged_in(self):
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        redirect_url = f'/admin/login/?next=/admin/status_summary'
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_access_status_summary_partner_logged_in(self):
        self.client.login(username=self.partner.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        redirect_url = f'/admin/login/?next=/admin/status_summary'
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_access_status_summary_admin_logged_in(self):

        appCt = random.randint(1, 10)
        appList = []

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=self.project))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

    def test_status_summary_group_random_app(self):
        appCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory())

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        #default applicant
        applicant = 'students'
        for groupType in self.groupTypes:
            response = self.client.get(f'/admin/status_summary/?group='+groupType)
            current_sem = [item for item in response.context.get("semester_support") if item[1] == config.CURRENT_SEMESTER]
            semester = current_sem[0][0]
            self.response_validation(response, groupType, semester, applicant, appList)

    def test_status_summary_group_random_proj(self):
        studentCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        studentList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory())

        for i in range(0, studentCt):
            studentList.append(StudentFactory())

            selectedProjCt = random.randint(1, projCt) - 1
            for projNum in random.sample(range(0, projCt), selectedProjCt):
                appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        # default
        applicant = 'students'
        for groupType in self.groupTypes:
            response = self.client.get(f'/admin/status_summary/?group='+groupType)
            self.assertEqual(response.status_code, 200)

            current_sem = [item for item in response.context.get("semester_support") if item[1] == config.CURRENT_SEMESTER]
            semester = current_sem[0][0]

            self.response_validation(response, groupType, semester, applicant, appList)

    def test_status_summary_semester(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)

        projList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        # default value
        groupType = 'student'
        applicant = 'students'
        for semester in self.semesters:
            response = self.client.get(f'/admin/status_summary/?semester='+semester+self.default_link_values)
            self.response_validation(response, groupType, semester, applicant, appList)

    def test_status_summary_group_semester(self):
        studentCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        studentList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, studentCt):
            studentList.append(StudentFactory())
            selectedProjCt = random.randint(1, projCt) - 1
            for projNum in random.sample(range(0, projCt), selectedProjCt):
                appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        #default applicant
        applicant = 'students'
        for groupType in self.groupTypes:
            for semester in self.semesters:
                response = self.client.get(f'/admin/status_summary/?group=' + groupType + '&semester=' + semester + self.default_link_values)
                self.response_validation(response, groupType, semester, applicant, appList)

    def test_status_summary_group_semester_applicant(self):
        studentCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        studentList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, studentCt):
            if i < studentCt//2:
                studentList.append(StudentFactory())
            else:
                ds = DataScholarFactory()
                studentList.append(StudentFactory(email_address=ds.email_address))

            selectedProjCt = random.randint(1, projCt) - 1
            for projNum in random.sample(range(0, projCt), selectedProjCt):
                appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    response = self.client.get(f'/admin/status_summary/?group=' + groupType + '&semester=' + semester+ '&applicant=' + applicant + self.default_link_values)
                    self.response_validation(response, groupType, semester, applicant, appList)

    def test_status_summary_group_semester_applicant_random_status(self):
        studentCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        studentList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, studentCt):
            if i < studentCt//2:
                studentList.append(StudentFactory())
            else:
                ds = DataScholarFactory()
                studentList.append(StudentFactory(email_address=ds.email_address))

            selectedProjCt = random.randint(1, projCt) - 1
            for projNum in random.sample(range(0, projCt), selectedProjCt):
                appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i], status = self.filters[random.randint(1, len(self.filters)-1)].upper()))

        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('admin:status_summary'))
        self.assertEqual(response.status_code, 200)

        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    response = self.client.get(f'/admin/status_summary/?group=' + groupType + '&semester=' + semester+ '&applicant=' + applicant + self.default_link_values)
                    self.response_validation(response, groupType, semester, applicant, appList)
