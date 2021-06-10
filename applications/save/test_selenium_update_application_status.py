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
# from students.tests.factories.datascholar import DataScholarFactory
# from students.tests.factories.studentprofile import StudentProfileaFactory
from projects.models import Semester, Project
from students.models import Student
from applications.models import Application

import random
import time
from bs4 import BeautifulSoup

import os

# Create your tests here.
class AppUpdateApplicationStatusTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        chromedriver = settings.WEBDRIVER
        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"

    @classmethod
    def setUp(cls):
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory(password=cls.password)
        cls.app_status_map = {k:v for k, v in Application.app_status_mapping.items()}

    ### START HELPER FUNCTIONS ###

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get(self.live_server_url)

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    ### END HELPER FUNCTIONS ###

    # # EC TO REVIEW
    # def basic_information_page_validation(self, loginUser, student, skillset):
    #     p = self.selenium.find_element_by_xpath("//h5[contains(text(),'Basic Information')]")
    #     self.assertEqual(p.text,"Basic Information")
    #
    #     basicInfoMap = {
    #         "Name"    : student.first_name + " " + student.last_name,
    #         "Email"   : getattr(loginUser, "email_address",getattr(loginUser,"email","")), # Login user's email address, UserFacory doesn't have attr email_address, instead it store email to attribute email
    #         "SID"     : student.student_id,
    #         "Major"   : student.major,
    #         "EGT"     : Student.egt_mapping[student.year], # need to convert to long NAME
    #         "College" : Student.college_mapping[student.college], # need to convert to LONG Name
    #         "Resume"  : student.resume_link
    #     }
    #
    #     # check on basic information; it may not have value for all the fields
    #     for pgElement in self.selenium.find_elements_by_xpath("//h5[contains(text(),\'Basic Information')]/following-sibling::p"):
    #         items = pgElement.text.split(": ")
    #         # check only return value on the field
    #         if(len(items) > 1):
    #             value = items[1].strip()
    #             #print(items[0], value,basicInfoMap[items[0]])
    #             self.assertEqual(value,basicInfoMap[items[0]])
    #
    #     # check on General Interest Statement
    #     p=self.selenium.find_element_by_xpath("//h5[contains(text(),\'General Interest Statement')]/following-sibling::p")
    #     self.assertEqual(p.text,student.general_question)
    #
    #     # check for skill set return
    #     if (not skillset == None):
    #         bfield = True
    #         for pgElement in self.selenium.find_elements_by_xpath("//div[@class='p-2 my-1']//td"):
    #             if (bfield):
    #                 skill = pgElement.text
    #             else:
    #                 skillLevel = next(k for k,v in Student.skill_levels_options.items() if v == pgElement.text)
    #                 #print(skill, skillLevel)
    #                 if (skillLevel.strip() == ""):
    #                     self.assertNotIn(skill,skillset.keys())
    #                 else:
    #                     self.assertEqual(skillLevel,skillset[skill])
    #             bfield = not bfield
    #
    #     # check on additional skills
    #     p=self.selenium.find_element_by_xpath("//h6[contains(text(),\'Additional Skills')]/following-sibling::p")
    #     self.assertEqual(p.text,student.additional_skills)
    # # EC TO REVIEW
    # def application_page_validation(self, answerList):
    #     for ans in answerList:
    #         searchStr = "//button[contains(text(),'" + ans.application.project.project_name  +"')]"
    #         button = self.selenium.find_element_by_xpath(searchStr)
    #         button.click()
    #
    #         app_questions = BeautifulSoup(self.selenium.find_element_by_class_name("application-question").get_attribute('innerHTML'), features="html.parser")
    #         self.assertEqual(ans.question.question_text, app_questions.find("h6").text)
    #         self.assertEqual(ans.answer_text, app_questions.find("textarea").text)

    def test_access_update_application_status_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

    def test_access_update_application_status_user_login(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('update_application_status')))

        expectedMsg = "Sorry, that action isn't supported."
        p=self.selenium.find_element_by_xpath("//h1[contains(text(),'400')]/following-sibling::p")
        self.assertEqual(expectedMsg, p.text)

    def test_access_update_application_status_partner_login(self):
        settings.CONSTANCE_CONFIG['APPLICATIONS_REVIEWABLE'] = (False, "Whether partners can review applications", bool)

        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('update_application_status')))

        expectedMsg = "Sorry, that action isn't supported."
        p = self.selenium.find_element_by_xpath("//h1[contains(text(),'400')]/following-sibling::p")
        self.assertEqual(expectedMsg, p.text)

    def test_access_update_application_status_as_partner_reviewable(self):

        settings.CONSTANCE_CONFIG['APPLICATIONS_REVIEWABLE'] = (True, "Whether partners can review applications", bool)

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
            comb = (random.randint(0,projCt-1),random.randint(0,studentCt-1))
            if comb in pair:
                continue
            pair.append(comb)

            proj = partnerProjList[comb[0]].project
            student_obj = studentList[comb[1]]
            status = app_status[random.randint(0,len(app_status)-1)]
            application = ApplicationFactory(project=proj, student=student_obj,status = status)
            appList.append(application)
            answerList.append(AnswerFactory(student=self.student_obj, application=application))

        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('update_application_status')))
        input("wait")
        expectedMsg = "Sorry, that action isn't supported."
        p = self.selenium.find_element_by_xpath("//h1[contains(text(),'400')]/following-sibling::p")
        self.assertEqual(expectedMsg, p.text)
        # expectedMsg = "Team Roster"
        # self.assertEqual(expectedMsg,self.selenium.find_element_by_id("team-roster").text)
        # self.team_roster_page_validation(self.partner_obj,partnerProjList,appList)

    def test_access_update_application_status_student_login(self):
        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('update_application_status')))

        expectedMsg = "Sorry, that action isn't supported."
        p = self.selenium.find_element_by_xpath("//h1[contains(text(),'400')]/following-sibling::p")
        self.assertEqual(expectedMsg, p.text)

    def test_access_update_application_status_admin_login(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('update_application_status')))

        expectedMsg = "Sorry, that action isn't supported."
        p = self.selenium.find_element_by_xpath("//h1[contains(text(),'400')]/following-sibling::p")
        self.assertEqual(expectedMsg, p.text)

    # def test_access_update_application_status_as_admin_with_profile(self):
    #     admin = AdminFactory(password=self.password)
    #     self.user_login(admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #     # Create profile
    #     student = StudentFactory(email_address = admin.email)
    #     ifield = ["first_name","last_name","student_id","major","resume_link","general_question", "additional_skills"]
    #     for j in range(0, len(ifield)) :
    #         self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))
    #
    #     bfield = ["college","year"]
    #     for j in range(0, len(bfield)) :
    #         Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))
    #
    #     skillset = {}
    #     for skill in Student.default_skills:
    #         skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
    #     for j in skillset:
    #         Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])
    #
    #     self.selenium.find_element_by_xpath("//input[@type='submit']").click()
    #
    #     # add application associate to the student
    #     appCt = random.randint(1, 10)
    #     answerList =[]
    #
    #     for i in range(0, appCt):
    #         proj = ProjectFactory()
    #         application = ApplicationFactory(project=proj,student=student)
    #         answerList.append(AnswerFactory(student=student, application=application))
    #
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #     self.application_page_validation(answerList)
    #
    # def test_access_update_application_status_as_user(self):
    #     self.user_login(self.user)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #     # Create profile
    #     student = StudentFactory()
    #     ifield = ["first_name","last_name","student_id","major","resume_link","general_question", "additional_skills"]
    #     for j in range(0, len(ifield)) :
    #         self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))
    #
    #     bfield = ["college","year"]
    #     for j in range(0, len(bfield)) :
    #         Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))
    #
    #     skillset = {}
    #     for skill in Student.default_skills:
    #         skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
    #     for j in skillset:
    #         Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])
    #
    #     self.selenium.find_element_by_xpath("//input[@type='submit']").click()
    #     self.basic_information_page_validation(self.user, student, skillset)
    #
    # def test_access_update_application_status_as_user_with_profile(self):
    #     user = UserFactory(password=self.password)
    #     self.user_login(user)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #     # Create profile
    #     student = StudentFactory(email_address = user.email)
    #     ifield = ["first_name","last_name","student_id","major","resume_link","general_question", "additional_skills"]
    #     for j in range(0, len(ifield)) :
    #         self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))
    #
    #     bfield = ["college","year"]
    #     for j in range(0, len(bfield)) :
    #         Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))
    #
    #     skillset = {}
    #     for skill in Student.default_skills:
    #         skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
    #     for j in skillset:
    #         Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])
    #
    #     self.selenium.find_element_by_xpath("//input[@type='submit']").click()
    #     #self.basic_information_page_validation(self.user, student, skillset)
    #
    #     # add application associate to the student
    #     appCt = random.randint(1, 10)
    #     answerList =[]
    #
    #     for i in range(0, appCt):
    #         proj = ProjectFactory()
    #         application = ApplicationFactory(project=proj,student=student)
    #         answerList.append(AnswerFactory(student=student, application=application))
    #
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #     self.application_page_validation(answerList)
    #
    # def test_access_update_application_status_login_as_partner(self):
    #     partner = UserFactory(password=self.password)
    #     partner_obj=PartnerFactory(email_address=partner.email,first_name=partner.first_name, last_name = partner.last_name)
    #
    #     projCt = random.randint(1, 10)
    #     partnerProjList = []
    #
    #     for i in range(0, projCt):
    #         partnerProjList.append( PartnerProjectInfoFactory(project=ProjectFactory(),partner=partner_obj))
    #
    #     self.user_login(partner)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #
    #     # NOT IMPLEMENTED YET?
    #     expectedMsg = "Applications are not yet open for review. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
    #     print(self.selenium.find_element_by_id("application-questions").text)
    #
    #     self.assertEqual(expectedMsg, self.selenium.find_element_by_id("application-questions").text)

    # def test_access_update_application_status_login_as_student(self):
    #     student = UserFactory(password=self.password)
    #     student_obj = StudentFactory(email_address=student.email,first_name=student.first_name, last_name = student.last_name)
    #
    #     # add application associate to the student
    #     appCt = random.randint(1, 10)
    #     answerList =[]
    #
    #     for i in range(0, appCt):
    #         proj = ProjectFactory()
    #         application = ApplicationFactory(project=proj,student=student_obj)
    #         answerList.append(AnswerFactory(student=student_obj, application=application))
    #
    #     self.user_login(student)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('update_application_status')))
    #
    #     self.application_page_validation(answerList)
