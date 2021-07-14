from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from constance import config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from factory_djoy import UserFactory
from projects.tests.factories.project import ProjectFactory
from applications.tests.factories.application import ApplicationFactory
from applications.tests.factories.answer import AnswerFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory

from students.models import Student
from projects.models import Project
from applications.models import Application

import random
import time
from bs4 import BeautifulSoup

# Create your tests here.
class AppIndexTest(StaticLiveServerTestCase):
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

    @classmethod
    def setUp(cls):
        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.admin = AdminFactory(password=cls.password)

        cls.sem_map = {k:v for k, v in Project.sem_mapping.items()}
        cls.app_status_map = {k:v for k, v in Application.app_status_mapping.items()}

    ### START HELPER FUNCTIONS ###

    def user_login(self, userObject):
        self.client.force_login(userObject)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.selenium.get(self.live_server_url)

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def basic_information_page_validation(self, loginUser, student, skillset):
        # h5 text attribute contains Basic Information
        p = self.selenium.find_element_by_xpath("//h5[contains(text(), 'Basic Information')]")

        # Check is exactly "Basic Information"
        self.assertEqual(p.text, "Basic Information")

        basicInfoMap = {
            "Name"    : f"{student.first_name} {student.last_name}",
            "Email"   : getattr(loginUser, "email_address", getattr(loginUser, "email", "")), # Login user's email address. UserFactory doesn't have the attribute email_address, instead it stores email as the attribute email
            "SID"     : student.student_id,
            "Major"   : student.major,
            "EGT"     : Student.egt_mapping[student.year], # Need to convert to long form
            "College" : Student.college_mapping[student.college], # Need to convert to long form
            "Resume"  : student.resume_link
        }

        # Check basic information. It may contain a superset or subset of these fields.
        for pgElement in self.selenium.find_elements_by_xpath("//h5[contains(text(),\'Basic Information')]/following-sibling::p"):
            items = pgElement.text.split(": ")
            if(len(items) > 1):
                value = items[1].strip()
                self.assertEqual(value, basicInfoMap[items[0]])

        # Check General Interest Statement
        p = self.selenium.find_element_by_xpath("//h5[contains(text(), \'General Interest Statement')]/following-sibling::p")
        self.assertEqual(p.text, student.general_question)

        # Check returned skill set
        if not skillset == None:
            bfield = True
            for pgElement in self.selenium.find_elements_by_xpath("//div[@class='p-2 my-1']//td"):
                if bfield:
                    skill = pgElement.text
                else:
                    skillLevel = next(k for k, v in Student.skill_levels_options.items() if v == pgElement.text)
                    if skillLevel.strip() == "":
                        self.assertNotIn(skill, skillset.keys())
                    else:
                        self.assertEqual(skillLevel, skillset[skill])
                bfield = not bfield

        # Check additional skills
        p = self.selenium.find_element_by_xpath("//h6[contains(text(), \'Additional Skills')]/following-sibling::p")
        self.assertEqual(p.text, student.additional_skills)

    def application_page_validation(self, answerList):
        for ans in answerList:
            searchStr = f"//button[contains(text(),'{ans.application.project.project_name}')]"
            button = self.selenium.find_element_by_xpath(searchStr)
            button.click()

            app_questions = BeautifulSoup(self.selenium.find_element_by_class_name("application-question").get_attribute('innerHTML'), features="html.parser")
            self.assertEqual(ans.question.question_text, app_questions.find("h6").text)
            self.assertEqual(ans.answer_text, app_questions.find("textarea").text)

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

            expectedSections = ["Partners", "Students"]
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

    ### END HELPER FUNCTIONS ###

    def test_access_application_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        self.assertEqual(self.logonRedirect, self.selenium.current_url)

    def test_access_application_user_login(self):
        self.user_login(self.user)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        signupRedirect = self.live_server_url + "/profile/signup"
        self.assertEqual(signupRedirect, self.selenium.current_url)

        expectedMsg = "Please create your student profile to view applications."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_application_partner_login(self):
        config.APPLICATIONS_REVIEWABLE = False
        self.user_login(self.partner)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        signupRedirect = f'{self.live_server_url}/'
        self.assertEqual(signupRedirect, self.selenium.current_url)

        expectedMsg = "You do not have any projects assigned to you. If this is an error, please contact ds-discovery@berkeley.edu."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_application_student_login(self):
        self.user_login(self.student)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        signupRedirect = self.live_server_url + reverse('app_index')
        self.assertEqual(signupRedirect, self.selenium.current_url)

        expectedMsg ="You haven't applied to any projects yet. You can apply to projects here."
        webelement = self.selenium.find_elements_by_class_name("p-2")
        self.assertEqual(webelement[len(webelement)-1].text, expectedMsg)

    def test_access_application_admin_login(self):
        self.user_login(self.admin)
        signupRedirect = self.live_server_url + "/"
        self.assertEqual(signupRedirect, self.selenium.current_url)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        signupRedirect = self.live_server_url + "/profile/signup"
        self.assertEqual(signupRedirect, self.selenium.current_url)

        expectedMsg="Please create your student profile to view applications."
        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual(expectedMsg, msg_html.find("div").text)

    def test_access_application_as_admin(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))

        # Create profile
        student = StudentFactory(email_address=self.admin.email)
        ifield = ["first_name", "last_name", "student_id", "major", "resume_link", "general_question", "additional_skills"]
        for j in range(0, len(ifield)):
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college", "year"]
        for j in range(0, len(bfield)):
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])
        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        self.basic_information_page_validation(self.admin, student, skillset)

    def test_access_application_as_admin_with_profile(self):
        self.user_login(self.admin)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))

        # Create profile
        student = StudentFactory(email_address=self.admin.email)
        ifield = ["first_name", "last_name", "student_id", "major", "resume_link", "general_question", "additional_skills"]
        for j in range(0, len(ifield)):
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college", "year"]
        for j in range(0, len(bfield)):
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])

        self.selenium.find_element_by_xpath("//input[@type='submit']").click()

        # add application associate to the student
        appCt = random.randint(1, 10)
        answerList =[]

        for i in range(0, appCt):
            proj = ProjectFactory()
            application = ApplicationFactory(project=proj, student=student)
            answerList.append(AnswerFactory(student=student, application=application))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        self.application_page_validation(answerList)

    def test_access_application_as_user(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))

        # Create profile
        student = StudentFactory(email_address=self.user.email)
        ifield = ["first_name", "last_name", "student_id", "major", "resume_link", "general_question",  "additional_skills"]
        for j in range(0, len(ifield)):
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college", "year"]
        for j in range(0, len(bfield)):
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])

        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        self.basic_information_page_validation(self.user, student, skillset)

    def test_access_application_as_user_with_profile(self):
        self.user_login(self.user)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        # Create profile
        student = StudentFactory(email_address=self.user.email)
        ifield = ["first_name", "last_name", "student_id", "major", "resume_link", "general_question", "additional_skills"]
        for j in range(0, len(ifield)):
            self.selenium.find_element_by_name(ifield[j]).send_keys(getattr(student, ifield[j]))

        bfield = ["college", "year"]
        for j in range(0, len(bfield)):
            Select(self.selenium.find_element_by_name(bfield[j])).select_by_value(getattr(student, bfield[j]))

        skillset = {}
        for skill in Student.default_skills:
            skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        for j in skillset:
            Select(self.selenium.find_element_by_name(j)).select_by_value(skillset[j])

        self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        self.basic_information_page_validation(self.user, student, skillset)


        # add application associate to the student
        appCt = random.randint(1, 10)
        answerList =[]

        for i in range(0, appCt):
            proj = ProjectFactory()
            application = ApplicationFactory(project=proj, student=student)
            answerList.append(AnswerFactory(student=student, application=application))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        self.application_page_validation(answerList)

    def test_access_application_login_as_partner_not_reviewable(self):
        config.APPLICATIONS_REVIEWABLE = False

        projCt = random.randint(1, 10)
        partnerProjList = []

        for i in range(0, projCt):
            partnerProjList.append(PartnerProjectInfoFactory(project=ProjectFactory(), partner=self.partner_obj))

        self.user_login(self.partner)
        self.selenium.get('%s%s' % (self.live_server_url,reverse('app_index')))

        expectedMsg = "Applications are not yet open for review. If you believe you have received this message in error, please email ds-discovery@berkeley.edu."
        self.assertEqual(expectedMsg, self.selenium.find_element_by_id("application-questions").text)

    def test_access_application_login_as_partner_reviewable(self):
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


    def test_access_application_login_as_student(self):
        # add application associate to the student
        appCt = random.randint(1, 10)
        answerList = []

        for i in range(0, appCt):
            proj = ProjectFactory()
            application = ApplicationFactory(project=proj, student=self.student_obj)
            answerList.append(AnswerFactory(student=self.student_obj, application=application))

        self.user_login(self.student)
        self.selenium.get('%s%s' % (self.live_server_url, reverse('app_index')))
        self.application_page_validation(answerList)