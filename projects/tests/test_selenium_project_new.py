from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
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
from constance import config

from projects.models import Semester, Project, get_default_skills
from students.models import Student

import json
import random
import time
import re
from faker import Faker
from bs4 import BeautifulSoup

import os

from django.contrib.auth.models import User

# Create your tests here.
class ProjectApplyTest(StaticLiveServerTestCase):
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

        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"

        sem_map = {k:v for k, v in Project.sem_mapping.items()}
        cls.short_current_semester = 'SP21'
        cls.current_semester = sem_map[cls.short_current_semester]
        config.CURRENT_SEMESTER = cls.current_semester

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
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email, first_name = cls.partner.first_name, last_name = cls.partner.last_name)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory()

    ### START HELPER FUNCTIONS ###

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get(self.live_server_url)

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def personal_information_page_validation(self, loginUser, newProjectName, newProjectOrganization):
        personalInfoMap = {
            "Name"    : loginUser.first_name + " " + loginUser.last_name,
            "Email"   : getattr(loginUser, "email_address", getattr(loginUser,"email","")),
        }

        p = self.selenium.find_element_by_xpath("//h5[contains(text(),'Personal Information')]")

        self.assertEqual(p.text, "Personal Information")

        for pgElement in self.selenium.find_elements_by_xpath("//h5[contains(text(),'Personal Information')]/following-sibling::p"):
            items = pgElement.text.split(": ")
            # check only return value on the field
            if(len(items) > 1):
                value = items[1].strip()
                self.assertEqual(value,personalInfoMap[items[0]])

        # verify applied project
        for pgElement in self.selenium.find_elements_by_xpath("//div[contains(@class, 'list-group-item')]"):
            text = pgElement.text
            role = text.split("Role: ", 1)[1]
            # skip Edit Button
            role = role.split()[0]
            project_name = text.split(" (")[0]
            organization = organization = re.search('\((.*)\)', text).group(1)

            self.assertEqual(project_name, newProjectName)
            self.assertEqual(role, "Sponsor")
            self.assertEqual(organization, newProjectOrganization)

    def basic_information_page_validation(self, loginUser, student, skillset):
        p = self.selenium.find_element_by_xpath("//h5[contains(text(),'Basic Information')]")
        self.assertEqual(p.text, "Basic Information")

        basicInfoMap = {
            "Name"    : student.first_name + " " + student.last_name,
            "Email"   : getattr(loginUser, "email_address", getattr(loginUser, "email", "")), # Login user's email address, UserFacory doesn't have attr email_address, instead it store email to attribute email
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
                self.assertEqual(value, basicInfoMap[items[0]])

        # check on General Interest Statement
        p=self.selenium.find_element_by_xpath("//h5[contains(text(),\'General Interest Statement')]/following-sibling::p")
        self.assertEqual(p.text, student.general_question)

        # check for skill set return
        if (not skillset == None):
            bfield = True
            for pgElement in self.selenium.find_elements_by_xpath("//div[@class='p-2 my-1']//td"):
                if (bfield):
                    skill = pgElement.text
                else:
                    skillLevel = next(k for k, v in Student.skill_levels_options.items() if v == pgElement.text)
                    if (skillLevel.strip() == ""):
                        self.assertNotIn(skill, skillset.keys())
                    else:
                        self.assertEqual(skillLevel, skillset[skill])
                bfield = not bfield

        # check on additional skills
        p=self.selenium.find_element_by_xpath("//h6[contains(text(),\'Additional Skills')]/following-sibling::p")
        self.assertEqual(p.text, student.additional_skills)

    def fill_in_project_application(self, loginUser):
        #fill in the app
        faker = Faker()
        project_profile_enter = {'id_email':loginUser.email,
            'id_first_name':loginUser.first_name,
            'id_last_name':loginUser.last_name,
            'id_organization':faker.sentence(),
            'id_organization_description':faker.paragraph(),
            'id_organization_website':faker.url(),
            'id_other_marketing_channel':faker.sentence(),
            'id_project_name':faker.sentence(),
            'id_other_project_category':"",
            'id_description':faker.paragraph(),
            'id_timeline':'Spring 2022',
            'id_project_workflow':faker.sentence(),
            'id_deliverable':faker.sentence(nb_words = 2),
            'id_other_num_students':str(random.randint(0, 10)),
            'id_technical_requirements':faker.sentence(),
            'id_additional_skills':faker.sentence(),
            'id_optional_q1':faker.sentence(),
            'id_optional_q2':faker.sentence(),
            'id_optional_q3':faker.sentence()
            }

        for k in project_profile_enter.keys():
            self.selenium.find_element_by_id(k).send_keys(project_profile_enter[k])

        # select by Value fields
        project_profile_select = {"id_marketing_channel": random.choice(['a','b','c','d','e','f']),
            'id_dataset_availability':random.choice(['True','False']),
            'id_num_students':random.choice(['a','b','c','d']),
            'id_cloud_creds':random.choice(['True','False']),
            'id_hce_intern':random.choice(['a','b','c']),
            'id_meet_regularly':random.choice(['True','False']),
            'id_survey_response':random.choice(['True','False']),
            'id_environment':random.choice(['True','False']),
            }

        skill_level = list(Student.skill_levels_options.keys())[1:]
        for skill in get_default_skills():
            project_profile_select[f"id_{skill}"] = random.choice(skill_level),

        for k in project_profile_select.keys():
            Select(self.selenium.find_element_by_id(k)).select_by_value(project_profile_select[k])

        print(project_profile_enter['id_project_name'], project_profile_enter['id_organization'])
        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        return project_profile_enter['id_project_name'], project_profile_enter['id_organization']

    ### END HELPER FUNCTIONS ###

    def test_access_list_projects_current_semester(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)

    def test_access_project_new_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)

    def test_access_project_new_user_login(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))

        # You must be a partner to create projects.
        expectedMsg = "You must be a partner to create projects."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_project_new_admin_login(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))
        # You must be a partner to create projects.
        expectedMsg = "You must be a partner to create projects."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_project_new_student_login(self):
        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))
        # You must be a partner to create projects.
        expectedMsg = "You must be a partner to create projects."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_project_new_partner_login(self):
        self.user_login(self.partner)
        urlRedirect = self.live_server_url + "/"
        self.assertEqual(urlRedirect, self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('new_project')))

        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'DS Discovery Project Application')
        newProjName, newProjOrganization = self.fill_in_project_application(self.partner)

        self.personal_information_page_validation(self.partner, newProjName, newProjOrganization)
