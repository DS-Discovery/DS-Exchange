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

from projects.models import Semester, Project
from students.models import Student

import json
import random
import time
import re
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

        chromedriver = r"C:\Users\eunic\Downloads\chromedriver_win32\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)

        cls.selenium = webdriver.Chrome(chromedriver, options=chrome_options)

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

    def user_login(self, userObject,selectedProjName):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))

        #self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))

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

    # def test_access_list_projects_current_semester(self):
    #     self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
    #     self.page_validation (projList)

    def test_access_project_apply_no_login(self):

        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        self.page_validation (projList)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_project_apply_user_login(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.user,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

    def test_access_project_apply_edit_profile_as_user(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.user,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

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
        # may fail due to additonal skills issue
        self.basic_information_page_validation(self.user, student, skillset)

    def test_access_project_apply_edit_profile_apply_as_user(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.user,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

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
        # may fail due to additonal skills issue
        #self.basic_information_page_validation(self.user, student, skillset)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        msg_html = BeautifulSoup(self.selenium.find_element_by_id("messages").get_attribute('innerHTML'), features="html.parser")
        expectedMsg = "Applications are currently closed. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
        self.assertEqual(expectedMsg,msg_html.find("div").text)

    def test_access_project_apply_admin_login(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.admin,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

    def test_access_project_apply_edit_profile_as_admin(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.admin,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

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
        # may fail due to additonal skills issue
        self.basic_information_page_validation(self.admin, student, skillset)

    def test_access_project_apply_edit_profile_apply_as_admin(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name
        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.admin,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        # Edit profile
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

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
        # may fail due to additonal skills issue
        #self.basic_information_page_validation(self.admin, student, skillset)

        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))
        msg_html = BeautifulSoup(self.selenium.find_element_by_id("messages").get_attribute('innerHTML'), features="html.parser")
        expectedMsg = "Applications are currently closed. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
        self.assertEqual(expectedMsg,msg_html.find("div").text)

    def test_access_project_apply_partner_login(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.partner,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))

        msg_html = BeautifulSoup(self.selenium.find_element_by_id("messages").get_attribute('innerHTML'), features="html.parser")
        expectedMsg = "You must be a student to apply to projects."
        self.assertEqual(expectedMsg,msg_html.find("div").text)

    def test_access_project_apply_student_login(self):
        projCt = random.randint(1, 10)
        projList = []
        for i in range(0, projCt):
            projList.append(ProjectFactory())
        selectedProjName = projList[0].project_name

        self.selenium.get('%s%s' % (self.live_server_url, reverse('list_projects')))
        # skip page validation
        #self.page_validation (projList)

        self.user_login(self.student,selectedProjName)
        signupRedirect = self.live_server_url + "/accounts/google/login/"
        self.assertEqual(signupRedirect,self.selenium.current_url)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('apply',kwargs={'project_name':selectedProjName})))

        msg_html = BeautifulSoup(self.selenium.find_element_by_id("messages").get_attribute('innerHTML'), features="html.parser")
        expectedMsg = "Applications are currently closed. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
        self.assertEqual(expectedMsg,msg_html.find("div").text)
