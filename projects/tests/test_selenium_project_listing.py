from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from django.conf import settings
from django.contrib import auth

from projects.tests.factories.project import ProjectFactory
from applications.tests.factories.application import ApplicationFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory

from factory_djoy import UserFactory
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

from django.contrib.auth.models import User

# Create your tests here.
class ProjectListingTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        cls.selenium = webdriver.Chrome(r'C:\Users\eunic\Downloads\chromedriver_win32\chromedriver.exe', options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"

        sem_map = {k:v for k, v in Project.sem_mapping.items()}
        cls.short_current_semester = 'SP21'
        cls.current_semester = sem_map[cls.short_current_semester]
        settings.CONSTANCE_CONFIG['CURRENT_SEMESTER'] = (cls.current_semester, "Current semester", str)

        #cls.selenium.implicitly_wait(5)

        cls.semesters = [s[0] for s in Semester.choices]
        cls.semesterCt = len(cls.semesters)

        cls.projMap = {"Project Description":"description", "Project Timeline":"timeline", "Project Workflow":"project_workflow",
        "Dataset":"dataset", "Deliverables":"deliverable", "Additional Skills":"additional_skills", "Technical Requirements":"technical_requirements"}

        cls.projectOrganizationStr = "Project Organization: "

    @classmethod
    def setUp(cls):
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory()

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def new_project_invalid_login_validation(self):
        self.selenium.find_element_by_xpath('//a[@href="newproject"]').click()

        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("You must be a partner to create projects.", msg_html.find("div").text)

    def page_validation(self, projList, appList = None):

        self.assertTrue(self.selenium.title == 'Data Science Discovery Program')

        projCatList = []
        projNameList = []
        optionList = []

        selectedProjList = [ x for x in projList if x.semester == self.short_current_semester]
        for proj in selectedProjList:
            projNameList.append(proj.project_name)
            for item in proj.project_category.split(";"):
                projCatList.append(item)

        projCatList = sorted(set(projCatList))
        projNameList = sorted(set(projNameList))

        categoryFilter = self.selenium.find_element_by_id("category-filter-select")
        options = [x for x in categoryFilter.find_elements_by_tag_name("option")]

        for element in options:
            option = element.get_attribute("value")
            if (option != ''):
                optionList.append(option)

        # validate "Project Category"
        self.assertEqual(optionList,projCatList)

        # validate "Project List"
        jsonText = self.selenium.find_element_by_id("projects-json").get_attribute("text")
        projects_json = json.loads(jsonText)['projects']
        i = 0

        for project in projects_json:
            self.assertEqual(project['project_name'],projNameList[i])
            #always return current semester
            self.assertEqual(project['semester'],self.current_semester)

            # validate the detail page
            project_button = self.selenium.find_element_by_id('project-'+ str(i))
            project_button.click()
            # if (i == 0):
            #     print(self.selenium.page_source)

            i = i + 1
            selectedProj = [x for x in selectedProjList if x.project_name == project['project_name']]

            self.assertEqual(len(selectedProj),1)
            selectedProj = selectedProj[0]

            descr_html = BeautifulSoup(self.selenium.find_element_by_id('description').get_attribute('innerHTML'), features="html.parser")
            self.assertEqual(project['project_name'],descr_html.find("h5").text)

            ## Skill Set
            skill_table = descr_html.find_all("table")
            for t in skill_table:
                bkey = True
                for cell in t.find_all("td"):
                    if bkey:
                        key = cell.text.rstrip()
                    else:
                        self.assertEqual(project['skillset'][key],cell.text)
                    bkey = not bkey

            bMatchNext = False
            matchText = ""
            for p in descr_html.find_all("p"):
                if (bMatchNext):
                    bMatchNext = False
                    self.assertEqual(matchText,p.text)

                if (p.text in self.projMap.keys()):
                    bMatchNext = True
                    matchText = getattr(selectedProj,self.projMap[p.text])

                #organization_description
                if (p.text.startswith(self.projectOrganizationStr)):
                    self.assertEqual(p.text.replace(self.projectOrganizationStr,''),getattr(selectedProj,"organization"))

                    bMatchNext = True
                    matchText = getattr(selectedProj,"organization_description")

            # check for project-sidebar
            projectSidebar_html = BeautifulSoup(self.selenium.find_element_by_id('project-sidebar').get_attribute('innerHTML'), features="html.parser")

            j = 0
            for s in projectSidebar_html.find_all('span'):
                #skip the last 2
                if (j < len(projectSidebar_html.find_all('span')) - 2):
                    self.assertIn(s.text,selectedProj.project_category.split(";"))
                if (j == len(projectSidebar_html.find_all('span')) - 2):
                    self.assertEqual(s.text,str(selectedProj.student_num))
                if (j == len(projectSidebar_html.find_all('span')) - 1):
                    if (appList == None):
                        self.assertEqual(s.text,str(0))
                    else:
                        selectedApps = [x for x in appList if x.project.project_name == project['project_name'] ]
                        self.assertEqual(s.text,str(len(selectedApps)))
                j = j + 1

        #input("Press Enter to continue...")
        time.sleep(5)

    def test_access_list_projects_current_semester(self):
        projCt = random.randint(1, 10)
        # appCt = random.randint(1, 10)
        # partnerCt = random.randint(1, 10)
        projList = []
        # appList = []
        # partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.short_current_semester))

        # for i in range(0, random.randint(1, 10)):
        #     partnerList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt) - 1]))

        # for i in range(0, appCt):
        #     appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        # print (partnerList)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.page_validation (projList)

    def test_access_list_projects_random_semester(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)
        partnerCt = random.randint(1, 10)
        projList = []
        appList = []
        partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        # for i in range(0, random.randint(1, 10)):
        #     partnerList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt) - 1]))

        # for i in range(0, appCt):
        #     appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        # print (partnerList)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.page_validation (projList)

    def test_access_list_projects_semester_app(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)
        partnerCt = random.randint(1, 10)
        projList = []
        appList = []
        partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.short_current_semester))

        # for i in range(0, random.randint(1, 10)):
        #     partnerList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt) - 1]))

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        # print (partnerList)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.page_validation (projList,appList)

    def test_access_list_projects_random_semester_app(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)
        partnerCt = random.randint(1, 10)
        projList = []
        appList = []
        partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        # for i in range(0, random.randint(1, 10)):
        #     partnerList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt) - 1]))

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        # print (partnerList)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.page_validation (projList,appList)

    def test_access_create_new_project_no_logon(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))

        newproj_button = self.selenium.find_element_by_xpath('//a[@href="newproject"]')
        newproj_button.click()

        self.assertEqual(self.logonRedirect,self.selenium.current_url)
        # segmentation fault

    def test_access_create_new_project_user_logon(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.new_project_invalid_login_validation()

    def test_access_create_new_project_admin_logon(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.new_project_invalid_login_validation()

    def test_access_create_new_project_student_logon(self):
        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.new_project_invalid_login_validation()

    def test_access_create_new_project_partner_logon(self):
        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))

        newproj_button = self.selenium.find_element_by_xpath('//a[@href="newproject"]')
        newproj_button.click()

        # only check the first line of the page.
        messages_html = BeautifulSoup(self.selenium.page_source, features="html.parser")
        self.assertEqual("DS Discovery Project Application",messages_html.find("h3").text)
