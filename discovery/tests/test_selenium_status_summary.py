from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib import admin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from factory_djoy import UserFactory
from projects.tests.factories.project import ProjectFactory
from applications.tests.factories.application import ApplicationFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory
from students.tests.factories.datascholar import DataScholarFactory

from projects.models import Semester, Project

import json
import random
import time
import re
from bs4 import BeautifulSoup

# Create your tests here.
class StatusSummaryTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        #default student
        #cls.groupTypes = ['Show statuses by students', 'Show status by projects']
        cls.groupTypes = ['student', 'project']
        #default current Semester (config.CURRENT_SEMESTER)

        cls.short_current_semester = next(k for k,v in Project.sem_mapping.items() if v ==config.CURRENT_SEMESTER)
        cls.semesters = [s[0] for s in Semester.choices]
        cls.semesterCt = len(cls.semesters)

        #default ALL IN
        cls.filters = ['Sub','Rni','Int','Rwi','Ofs','Ofr','Ofa']
        cls.filterStates = ['IN','OUT']
        #default 'students'
        cls.applicantTypes = ['students', 'scholars']

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        chromedriver = settings.WEBDRIVER
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)

        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/admin/login/?next=/admin/status_summary"

        cls.projMap = {"Project Description":"description", "Project Timeline":"timeline", "Project Workflow":"project_workflow",
        "Dataset":"dataset", "Deliverables":"deliverable", "Additional Skills":"additional_skills", "Technical Requirements":"technical_requirements"}

        cls.projectOrganizationStr = "Project Organization: "

        cls.table_column_student= ['Student',"First_Name","Last_Name","Sub","Rni","Int","Rwi","Ofs","Ofr","Ofa","Total"]
        cls.table_column_project= ['Project',"Contact","Sub","Rni","Int","Rwi","Ofs","Ofr","Ofa","Total"]

    @classmethod
    def setUp(cls):
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory(password=cls.password)

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def new_project_invalid_login_validation(self):
        self.selenium.find_element_by_xpath('//a[@href="newproject"]').click()

        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("You must be a partner to create projects.", msg_html.find("div").text)

    def page_validation(self, groupType, semester, applicant, appList, partnerProjectList, filterArrayDict=None):

        self.assertTrue(self.selenium.title == 'Status summary | Django site admin')

        # TBUpdated once the filter is implemented
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

        Select(self.selenium.find_element_by_xpath("//select[@name='group']")).select_by_value(groupType)
        Select(self.selenium.find_element_by_xpath("//select[@name='semester']")).select_by_value(semester)
        Select(self.selenium.find_element_by_xpath("//select[@name='applicant']")).select_by_value(applicant)
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        #print(self.selenium.page_source)

        table_html = BeautifulSoup(self.selenium.find_elements_by_class_name('table-container')[0].get_attribute('innerHTML'), features="html.parser")

        table = []
        for row in table_html.find_all('tr'):
            entry = {}
            td_tags = row.find_all('td')
            i = 0
            for td_tag in td_tags:
                if (groupType == 'student') :
                    entry[self.table_column_student[i]] = td_tag.text
                else :
                    entry[self.table_column_project[i]] = td_tag.text
                i = i + 1

            if (len(entry)) > 0:
                table.append(entry)

        qualifiedAppList = []
        qualifiedSet = set()
        # compute the expected Total rows
        for j in appList:
            if j.project.semester == semester and j.status in selectedFilterSet:
                if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                    # print(j.project.semester,j.status,j.student.email_address,j.project.project_name)
                    qualifiedAppList.append(j)

        #table length remove the header row
        if len(qualifiedAppList) > 0:
            if groupType == 'student':
                for j in qualifiedAppList:
                    qualifiedSet.add(j.student.email_address)

                # Return only applied student
                for i in table:
                    self.assertIn(i['Student'], qualifiedSet)
                    statusList= []
                    expectedRowCt = 0
                    for j in appList:
                        if j.student.email_address == i['Student'] and j.project.semester == semester:
                            if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                                expectedRowCt = expectedRowCt + 1
                                statusList.append(j.status)

                    if expectedRowCt > 0:
                        self.assertEqual(i['Total'], str(expectedRowCt))
                        for k in self.filters:
                            self.assertEqual(i[k], str(statusList.count(k.upper())))
            else: # groupType == 'project'
                for j in qualifiedAppList:
                    qualifiedSet.add(j.project.project_name)

                for i in table:
                    contactList=[]
                    self.assertIn(i['Project'], qualifiedSet)
                    # check with partnerproejctList
                    if  not partnerProjectList == None:
                        for j in partnerProjectList:
                            if j.project.project_name == i["Project"]:
                                contactList.append(j.partner.email_address)

                        if (len(contactList) == 0):
                            self.assertEqual("—",i['Contact'])
                        else:
                            contactList.sort()
                            tableContactList = i['Contact'].strip().split(", ")
                            tableContactList.sort()
                            self.assertEqual(contactList,tableContactList)

                    statusList = []
                    expectedRowCt = 0
                    for j in appList:
                        if j.project.project_name == i['Project'] and j.project.semester == semester:
                            if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
                                expectedRowCt = expectedRowCt + 1
                                statusList.append(j.status)

                    if expectedRowCt > 0:
                        self.assertEqual(i['Total'], str(expectedRowCt))
                        for k in self.filters:
                            self.assertEqual(i[k], str(statusList.count(k.upper())))

        if (len(qualifiedSet) > 0):
            self.assertEqual(len(table), len(qualifiedSet))

    def test_access_status_summary_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    # def test_access_status_summary_logon_by_keys(self):
    #     self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
    #     self.assertEqual(self.logonRedirect,self.selenium.current_url)
    #
    #     self.selenium.find_element_by_id("id_username").send_keys(self.admin.username)
    #     self.selenium.find_element_by_id("id_password").send_keys(self.password)
    #     print(self.admin.username)
    #     print(self.password)
    #     print(self.admin.password)
    #
    #     input("test_access_status_summary_logon_by_keys")
    #     # TBA error cannot logon got error
    #     self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def test_access_status_summary_user_login(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_status_summary_partner_login(self):
        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_status_summary_student_login(self):
        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_status_summary_admin_login(self):
        self.user_login(self.admin)
        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertTrue(self.selenium.title == 'Status summary | Django site admin')

    def test_status_summary_group_random_app(self):
        appCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        projList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory())

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        #default applicant
        applicant = 'students'
        semester = self.short_current_semester
        for groupType in self.groupTypes:
            self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
            self.page_validation(groupType, semester, applicant, appList, None)

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

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        # default
        applicant = 'students'
        semester = self.short_current_semester
        for groupType in self.groupTypes:
            self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
            self.page_validation(groupType, semester, applicant, appList, None)

    def test_status_summary_semester(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)

        projList = []
        appList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        # default
        groupType = 'student'
        applicant = 'students'
        for semester in self.semesters:
            self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
            self.page_validation(groupType, semester, applicant, appList, None)

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

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        #default applicant
        applicant = 'students'
        for groupType in self.groupTypes:
            for semester in self.semesters:
                self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
                self.page_validation(groupType, semester, applicant, appList, None)

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

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
                    self.page_validation(groupType, semester, applicant, appList, None)

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

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
                    self.page_validation(groupType, semester, applicant, appList, None)

    def test_status_summary_group_semester_applicant_partner_random_status(self):
        studentCt = random.randint(1, 10)
        projCt = random.randint(1, 10)
        partnerProjCt = random.randint(1, 10)
        projList = []
        studentList = []
        appList = []
        partnerProjectList= []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0,partnerProjCt):
            partnerProjectList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt)-1]))

        for i in range(0, studentCt):
            if i < studentCt//2:
                studentList.append(StudentFactory())
            else:
                ds = DataScholarFactory()
                studentList.append(StudentFactory(email_address=ds.email_address))

            selectedProjCt = random.randint(1, projCt) - 1
            for projNum in random.sample(range(0, projCt), selectedProjCt):
                appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i], status = self.filters[random.randint(1, len(self.filters)-1)].upper()))

        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))

        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
                    self.page_validation(groupType, semester, applicant, appList, partnerProjectList)
