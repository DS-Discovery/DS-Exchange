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
from constance import config

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

        # default student
        cls.groupTypes = ['student', 'project']
        # default current Semester (config.CURRENT_SEMESTER)

        cls.short_current_semester = next(k for k,v in Project.sem_mapping.items() if v == config.CURRENT_SEMESTER)
        cls.semesters = [s[0] for s in Semester.choices]
        cls.semesterCt = len(cls.semesters)

        # default ALL IN
        cls.filters = ['Sub','Rni','Int','Rwi','Ofs','Ofr','Ofa']
        cls.filterTypes = ['ANY', 'ALL']
        # default 'students'
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

    ### START HELPER FUNCTIONS ###

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def new_project_invalid_login_validation(self):
        self.selenium.find_element_by_xpath('//a[@href="newproject"]').click()

        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("You must be a partner to create projects.", msg_html.find("div").text)

    def page_validation(self, groupType, semester, applicant, appList, partnerProjectList, filterType="ANY", filters=None):
        self.assertTrue(self.selenium.title == 'Status summary | Django site admin')

        selectedFilterSet = []
        if not filters == None:
            for i in filters:
                selectedFilterSet.append(i)

        if len(selectedFilterSet) == 0:
            selectedFilterSet = self.filters.copy()
            self.selenium.find_element_by_id("showSelect").click()
        else :
            for x in selectedFilterSet:
                self.selenium.find_element_by_name(x).click()

        selectedFilterSet = [x.upper() for x in selectedFilterSet]

        Select(self.selenium.find_element_by_xpath("//select[@name='group']")).select_by_value(groupType)
        Select(self.selenium.find_element_by_xpath("//select[@name='semester']")).select_by_value(semester)
        Select(self.selenium.find_element_by_xpath("//select[@name='applicant']")).select_by_value(applicant)
        Select(self.selenium.find_element_by_xpath("//select[@name='any_all']")).select_by_value(filterType)
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

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
                    qualifiedAppList.append(j)

        #table length remove the header row
        if len(qualifiedAppList) > 0:
            if groupType == 'student':
                for j in qualifiedAppList:
                    email = j.student.email_address
                    valid = True
                    if (filterType == 'ALL'):
                        appStatus = [x.status for x in qualifiedAppList if x.student.email_address == email]
                        # set to unique
                        appStatus = list(set(appStatus))
                        if (len(appStatus) != len(selectedFilterSet)):
                            valid = False

                    if (valid == True):
                        qualifiedSet.add(email)

                if qualifiedSet:
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
                else:
                    # empty table
                    self.assertEqual(len(table), 1)
                    self.assertEqual(table[0]['Student'], '—')

            else: # groupType == 'project'
                for j in qualifiedAppList:
                    proj = j.project.project_name
                    valid = True
                    if (filterType == 'ALL'):
                        appStatus = [x.status for x in qualifiedAppList if x.project.project_name == proj]
                        # set to unique
                        appStatus = list(set(appStatus))
                        if (len(appStatus) != len(selectedFilterSet)):
                            valid = False

                    if(valid == True):
                        qualifiedSet.add(proj)
                if qualifiedSet:
                    for i in table:
                        contactList = []
                        self.assertIn(i['Project'], qualifiedSet)
                        # check with partnerprojectList
                        if  not partnerProjectList == None:
                            for j in partnerProjectList:
                                if j.project.project_name == i["Project"]:
                                    contactList.append(j.partner.email_address)

                            if (len(contactList) == 0):
                                self.assertEqual("—", i['Contact'])
                            else:
                                contactList.sort()
                                tableContactList = i['Contact'].strip().split(", ")
                                tableContactList.sort()
                                self.assertEqual(contactList, tableContactList)

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
                        if (len(table) != len(qualifiedSet)):
                            print(appList)
                        self.assertEqual(len(table), len(qualifiedSet))
                else:
                    # empty table
                    self.assertEqual(len(table), 1)
                    self.assertEqual(table[0]['Project'], '—')

    ### END HELPER FUNCTIONS ###

    def test_access_status_summary_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_status_summary_user_login(self):
        self.user_login(self.user)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)
        expectedMsg = "You are authenticated as " + self.user.username +", but are not authorized to access this page. Would you like to login to a different account?"
        self.assertEqual(expectedMsg,self.selenium.find_element_by_class_name('errornote').text)

    def test_access_status_summary_partner_login(self):
        self.user_login(self.partner)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)
        expectedMsg = "You are authenticated as " + self.partner.username +", but are not authorized to access this page. Would you like to login to a different account?"
        self.assertEqual(expectedMsg, self.selenium.find_element_by_class_name('errornote').text)

    def test_access_status_summary_student_login(self):
        self.user_login(self.student)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)
        expectedMsg = "You are authenticated as " + self.student.username +", but are not authorized to access this page. Would you like to login to a different account?"
        self.assertEqual(expectedMsg, self.selenium.find_element_by_class_name('errornote').text)

    def test_access_status_summary_admin_login(self):
        self.user_login(self.admin)
        self.assertTrue(self.selenium.title == 'Site administration | Django site admin')
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        self.assertTrue(self.selenium.title == 'Status summary | Django site admin')

    def test_access_status_summary_admin_login_from_admin_page(self):
        self.user_login(self.admin)
        self.assertTrue(self.selenium.title == 'Site administration | Django site admin')
        self.selenium.find_element_by_link_text("Status summary").click()
        # check the settings
        elements = {'group':'student',
                    'semester':self.short_current_semester,
                    'applicant':'students',
                    'any_all':"ANY"}
        for k,v in elements.items():
            path = "//select[@name='"+ k + "']"
            self.assertEqual(v,Select(self.selenium.find_element_by_xpath(path)).first_selected_option.get_attribute("value"))

        for x in self.filters :
            self.assertTrue(self.selenium.find_element_by_name(x).is_selected())

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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        #default applicant
        applicant = 'students'
        semester = self.short_current_semester

        for groupType in self.groupTypes:
            self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))

        # default
        applicant = 'students'
        semester = self.short_current_semester
        filter = "all"
        for groupType in self.groupTypes:
            self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))

        # default
        groupType = 'student'
        applicant = 'students'
        # click select all as default is none
        self.selenium.find_element_by_id("showSelect").click()
        for semester in self.semesters:
            self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))

        # default applicant
        applicant = 'students'
        # click select all as default is none
        self.selenium.find_element_by_id("showSelect").click()
        for groupType in self.groupTypes:
            for semester in self.semesters:
                self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        # click select all as default is none
        self.selenium.find_element_by_id("showSelect").click()
        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        # click select all as default is none
        self.selenium.find_element_by_id("showSelect").click()
        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
                    self.page_validation(groupType, semester, applicant, appList, partnerProjectList)

    def test_status_summary_group_semester_applicant_partner_filter_random_status(self):
        studentCt = random.randint(1, 15)
        projCt = random.randint(1, 15)
        partnerProjCt = random.randint(1, 15)
        projList = []
        studentList = []
        appList = []
        partnerProjectList= []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, partnerProjCt):
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
        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
        for groupType in self.groupTypes:
            for semester in self.semesters:
                for applicant in self.applicantTypes:
                    for filterType in self.filterTypes:
                        self.selenium.get('%s%s' % (self.live_server_url, reverse('admin:status_summary')))
                        self.page_validation(groupType, semester, applicant, appList, partnerProjectList,filterType, random.sample(self.filters, random.randint(1, len(self.filters)-1)))
