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
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory

from factory_djoy import UserFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory
from students.tests.factories.datascholar import DataScholarFactory
from students.tests.factories.studentprofile import StudentProfileFactory
from projects.models import Semester, Project
from students.models import Student

import random
import time
from bs4 import BeautifulSoup

import os
import re

# Create your tests here.
class LoginCallbackTest(StaticLiveServerTestCase):
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

        chromedriver = r"C:\Users\eunic\Downloads\chromedriver_win32\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)

        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"

    @classmethod
    def setUp(cls):
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email,first_name= cls.partner.first_name, last_name = cls.partner.last_name)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email,first_name= cls.student.first_name, last_name = cls.student.last_name)

        cls.admin = AdminFactory(password=cls.password)

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    # def new_project_invalid_login_validation(self):
    #     self.selenium.find_element_by_xpath('//a[@href="newproject"]').click()
    #
    #     msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
    #     self.assertEqual("You must be a partner to create projects.", msg_html.find("div").text)

    def personal_information_page_validation(self,loginUser,pprojList= None):
        #print(self.selenium.page_source)
        personalInfoMap = {
            "Name"    : loginUser.first_name + " " + loginUser.last_name,
            "Email"   : getattr(loginUser, "email_address",getattr(loginUser,"email","")),
        }
        p = self.selenium.find_element_by_xpath("//h5[contains(text(),'Personal Information')]")

        self.assertEqual(p.text,"Personal Information")

        for pgElement in self.selenium.find_elements_by_xpath("//h5[contains(text(),'Personal Information')]/following-sibling::p"):
            items = pgElement.text.split(": ")
            # check only return value on the field
            if(len(items) > 1):
                value = items[1].strip()
                #print(items[0], value,personalInfoMap[items[0]])
                self.assertEqual(value,personalInfoMap[items[0]])

        # verify Projects
        if (pprojList != None) :
            for pgElement in self.selenium.find_elements_by_xpath("//div[contains(@class, 'list-group-item')]"):
                text = pgElement.text
                role = text.split("Role: ",1)[1]
                project_name = text.split(" (")[0]
                organization = organization = re.search('\((.*)\)',text).group(1)

                for x in pprojList:
                    if (x.project.project_name == project_name):
                        selectedPproj = x
                        break

                self.assertNotEqual(selectedPproj,None)
                self.assertEqual(role,selectedPproj.role)
                self.assertEqual(organization,selectedPproj.project.organization)

    def basic_information_page_validation(self, loginUser, student, skillset):
        p = self.selenium.find_element_by_xpath("//h5[contains(text(),'Basic Information')]")
        self.assertEqual(p.text,"Basic Information")

        basicInfoMap = {
            "Name"    : student.first_name + " " + student.last_name,
            "Email"   : getattr(loginUser, "email_address",getattr(loginUser,"email","")), # Login user's email address, UserFacory doesn't have attr email_address, instead it store email to attribute email
            "SID"     : student.student_id,
            "Major"   : student.major,
            "EGT"     : Student.egt_mapping[student.year], # need to convert to long NAME
            "College" : Student.college_mapping[student.college], # need to convert to LONG Name
            "Resume"  : student.resume_link
        }

        # check on basic information; it may not have value for all the fields
        for pgElement in self.selenium.find_elements_by_xpath("//h5[contains(text(),\'Basic Information')]/following-sibling::p"):
            items = pgElement.text.split(": ")
            # check only return value on the field
            if(len(items) > 1):
                value = items[1].strip()
                #print(items[0], value,basicInfoMap[items[0]])
                self.assertEqual(value,basicInfoMap[items[0]])

        # check on General Interest Statement
        p=self.selenium.find_element_by_xpath("//h5[contains(text(),\'General Interest Statement')]/following-sibling::p")
        self.assertEqual(p.text,student.general_question)

        # check for skill set return
        if (not skillset == None):
            bfield = True
            for pgElement in self.selenium.find_elements_by_xpath("//div[@class='p-2 my-1']//td"):
                if (bfield):
                    skill = pgElement.text
                else:
                    skillLevel = next(k for k,v in Student.skill_levels_options.items() if v == pgElement.text)
                    #print(skill, skillLevel)
                    if (skillLevel.strip() == ""):
                        self.assertNotIn(skill,skillset.keys())
                    else:
                        self.assertEqual(skillLevel,skillset[skill])
                bfield = not bfield

        # check on additional skills
        p=self.selenium.find_element_by_xpath("//h6[contains(text(),\'Additional Skills')]/following-sibling::p")
        self.assertEqual(p.text,student.additional_skills)

    def test_access_login_callback_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_login_callback_user_login(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("Please complete your student profile.", msg_html.find("div").text)

    def test_access_login_callback_partner_login(self):
        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        # show personal information page
        self.personal_information_page_validation(self.partner)

    def test_access_login_callback_student_login(self):
        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        # show profile page directly information page
        self.basic_information_page_validation(self.student,self.student_obj, None)

    def test_access_login_callback_admin_login(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        # check for banner message:
        # Please complete your student profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("Please complete your student profile.", msg_html.find("div").text)

    def test_access_login_callback_edit_profile_as_user(self):
        self.user_login(self.user)
        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("Please complete your student profile.", msg_html.find("div").text)

        student = StudentFactory()
        ifield = ["first_name","last_name","student_id","major","resume_link","general_question", "additional_skills"]
        for j in range(0, len(ifield)) :
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college","year"]
        for j in range(0, len(bfield)) :
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])

        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        # print(self.selenium.page_source)
        self.basic_information_page_validation(self.user, student, skillset)

    def test_access_login_callback_as_partner(self):

        partner = UserFactory(password=self.password)
        partner_obj=PartnerFactory(email_address=partner.email,first_name=partner.first_name, last_name = partner.last_name)

        projCt = random.randint(1, 10)
        partnerProjList = []

        for i in range(0, projCt):
            partnerProjList.append( PartnerProjectInfoFactory(project=ProjectFactory(),partner=partner_obj))

        self.user_login(partner)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))

        #show personal information page
        self.personal_information_page_validation(partner,partnerProjList)

    def test_access_login_callback_as_student(self):

        student = UserFactory(password=self.password)
        student_obj = StudentFactory(email_address=student.email,first_name=student.first_name, last_name = student.last_name)

        # add application associate to the student
        appCt = random.randint(1, 10)
        appList = []

        for i in range(1, appCt):
            appList.append(ApplicationFactory(project=ProjectFactory(),student=student_obj))

        self.user_login(student)

        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))

        # show Basic Information directly information page
        self.basic_information_page_validation(student,student_obj, student_obj._skills)

    def test_access_login_callback_edit_profile_as_admin(self):
        self.user_login(self.admin)
        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('login_callback')))
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("Please complete your student profile.", msg_html.find("div").text)

        student = StudentFactory()
        ifield = ["first_name","last_name","student_id","major","resume_link","general_question", "additional_skills"]
        for j in range(0, len(ifield)) :
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college","year"]
        for j in range(0, len(bfield)) :
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])

        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        self.basic_information_page_validation(self.admin, student, skillset)
