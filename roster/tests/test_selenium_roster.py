from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib import admin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from constance import config

from projects.tests.factories.project import ProjectFactory
from applications.tests.factories.application import ApplicationFactory
from applications.tests.factories.answer import AnswerFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory

from factory_djoy import UserFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory

from projects.models import Semester, Project
from students.models import Student
from applications.models import Application

import random
import time
from bs4 import BeautifulSoup

import os

# Create your tests here.
class RosterTest(StaticLiveServerTestCase):
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

        chromedriver = settings.WEBDRIVER
        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"
        cls.sem_map = {k:v for k, v in Project.sem_mapping.items()}
        cls.app_status_map = {k:v for k, v in Application.app_status_mapping.items()}

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

        self.selenium.get('%s%s' % (self.live_server_url,reverse('display_student_team_roster')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()


    ### END HELPER FUNCTIONS ###

    def team_roster_page_validation(self, loginUser, partnerProjList, appList):

        # go thru the project list, check for the project and applicants Information
        # Not downloading and verifying CSV

        for proj in partnerProjList:

            Select(self.selenium.find_element_by_name("project_wanted")).select_by_visible_text(proj.project.project_name)
            self.selenium.find_element_by_id("team-roster").click()

            # verify "application-questions -- Project related page"
            messages_html = BeautifulSoup(self.selenium.find_element_by_id("application-questions").get_attribute('innerHTML'), features="html.parser")

            #proj title format "Team Roster for <proj name>"
            expectedMsg = "Team Roster for " + proj.project.project_name
            self.assertEqual(messages_html.find("h3").text,expectedMsg)

            expectedSections = ["Partners","Students"]
            for i, webElement in enumerate(messages_html.find_all("h4")):
                self.assertEqual(expectedSections[i],webElement.text)

            partnerInfo = loginUser.first_name + " " + loginUser.last_name + ": " + loginUser.email_address

            accepted_applicants = []

            # search application by project name
            app = [x for x in appList if x.project.project_name == proj.project.project_name and x.status == "OFA"]
            for x in app:
                accepted_applicants.append(x.student.first_name + " " + x.student.last_name + ": " + x.student.email_address)

            if (len(accepted_applicants) == 0):
                accepted_applicants.append("None yet!")

            list_items = messages_html.find_all("li")
            expectedMsg = [partnerInfo]
            self.assertEqual(partnerInfo,list_items[0].text)
            for webElement in list_items[1:]:
                self.assertIn(webElement.text,accepted_applicants)

            # Assume CSV correct
            #self.selenium.find_element_by_class_name("appButton").click()

            applicants = []

            # search application by project name
            app = [x for x in appList if x.project.project_name == proj.project.project_name]
            for x in app:
                applicants.append(x.student.first_name + " " + x.student.last_name)

            # check for all applicants
            for webElement in self.selenium.find_elements_by_name("selected_applicant"):
                self.assertIn(webElement.text,applicants)

                studentapp = next(x for x in app if x.student.first_name + " " + x.student.last_name == webElement.text )
                student = studentapp.student

                webElement.click()

                # verify "application-questions -- Student info"
                messages_html = BeautifulSoup(self.selenium.find_element_by_id("application-questions").get_attribute('innerHTML'), features="html.parser")

                # first p == description 2nd p == additional information
                expected = [student.general_question, student.additional_skills]
                for i, w in enumerate(messages_html.find_all("p")[1:]):
                    self.assertEqual(expected[i],w.text)

                # verify student basic info
                messages_html = BeautifulSoup(self.selenium.find_element_by_id("app-sidebar").get_attribute('innerHTML'), features="html.parser")
                # order Name, Email. Major, Graduation Term
                expected = [webElement.text, student.email_address, student.major, self.sem_map[student.year]]
                for i, w in enumerate(messages_html.find_all("p")):
                    self.assertEqual(w.text.split(': ')[1],expected[i])

                # verify application status button state
                btn_id = "btn-" + studentapp.status
                if not (studentapp.status == "SUB"):
                    self.assertIn("disabled=",self.selenium.find_element_by_id(btn_id).get_attribute('outerHTML'))

    def test_access_roster_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('display_student_team_roster')))
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

    def test_access_roster_user_login(self):
        self.user_login(self.user)
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('display_student_team_roster')))

        expectedMsg = "You must be a member of a project team to view the roster."
        p=self.selenium.find_element_by_class_name("alert-info")
        self.assertEqual(expectedMsg, p.text)

    def test_access_roster_partner_login(self):
        self.user_login(self.partner)
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('display_student_team_roster')))

        expectedMsgs = ["Partners view the roster in applications.",
        "You do not have any projects assigned to you. If this is an error, please contact ds-discovery@berkeley.edu."]
        for i,x in enumerate(self.selenium.find_elements_by_class_name("alert-info")):
            self.assertEqual(x.text,expectedMsgs[i])

    def test_access_roster_student_login(self):
        self.user_login(self.student)
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('display_student_team_roster')))

        expectedMsg = "You must be a member of a project team to view the roster."
        p=self.selenium.find_element_by_class_name("alert-info")
        self.assertEqual(expectedMsg, p.text)

    def test_access_roster_admin_login(self):
        self.user_login(self.admin)
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('display_student_team_roster')))

        expectedMsg = "You must be a member of a project team to view the roster."
        p=self.selenium.find_element_by_class_name("alert-info")
        self.assertEqual(expectedMsg, p.text)

    def test_access_roster_partner_with_projects_login_not_reviewable(self):
        projCt = random.randint(1, 10)
        partnerProjList = []
        partner =  UserFactory(password=self.password)
        partner_obj =  PartnerFactory(email_address=partner.email)

        for i in range(0, projCt):
            partnerProjList.append(PartnerProjectInfoFactory(project=ProjectFactory(), partner=partner_obj))

        config.APPLICATIONS_REVIEWABLE = False
        self.user_login(partner)

        self.assertEqual(self.logonRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('display_student_team_roster')))

        expectedMsgs = ["Partners view the roster in applications."]
        for i,x in enumerate(self.selenium.find_elements_by_class_name("alert-info")):
            self.assertEqual(x.text,expectedMsgs[i])
        expectedMsg = "Applications are not yet open for review. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
        self.assertEqual(expectedMsg, self.selenium.find_element_by_id("application-questions").text)

    def test_access_roster_partner_with_projects_login_reviewable(self):
        config.APPLICATIONS_REVIEWABLE = True
        app_status = list(self.app_status_map.keys())

        projCt = random.randint(1, 10)
        appCt = random.randint(10,20)
        studentCt = random.randint(1,20)
        partnerProjList = []
        studentList = []
        answerList = []
        appList = []

        for i in range(0,studentCt):
            studentList.append(StudentFactory())

        for i in range(0, projCt):
            partnerProjList.append(PartnerProjectInfoFactory(project=ProjectFactory(), partner=self.partner_obj))

        pair = []
        for i in range(0, appCt):
            comb = (random.randint(0, projCt-1),random.randint(0, studentCt-1))
            if comb in pair:
                continue
            pair.append(comb)

            proj = partnerProjList[comb[0]].project
            student_obj = studentList[comb[1]]
            status = app_status[random.randint(0, len(app_status)-1)]
            application = ApplicationFactory(project=proj, student=student_obj, status = status)
            appList.append(application)
            answerList.append(AnswerFactory(student=self.student_obj, application=application))

        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        expectedMsg = "Team Roster"
        self.assertEqual(expectedMsg,self.selenium.find_element_by_id("team-roster").text)
        self.team_roster_page_validation(self.partner_obj, partnerProjList, appList)
