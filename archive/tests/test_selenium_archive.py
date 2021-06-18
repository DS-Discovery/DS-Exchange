from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.conf import settings

from projects.tests.factories.project import ProjectFactory
from applications.tests.factories.application import ApplicationFactory
from projects.models import Semester, Project
from constance import config

import json
import random
from bs4 import BeautifulSoup

# Create your tests here.
class ArchiveTest(StaticLiveServerTestCase):
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

        sem_map = {k:v for k, v in Project.sem_mapping.items()}
        cls.short_current_semester = 'SP21'
        cls.current_semester = sem_map[cls.short_current_semester]
        config.CURRENT_SEMESTER = cls.current_semester

        cls.semesters = [s[0] for s in Semester.choices]
        cls.semesterCt = len(cls.semesters)

        cls.projMap = {"Project Description":"description", "Project Timeline":"timeline", "Project Workflow":"project_workflow",
        "Dataset":"dataset", "Deliverables":"deliverable", "Additional Skills":"additional_skills", "Technical Requirements":"technical_requirements"}

        cls.projectOrganizationStr = "Project Organization: "

    ### START HELPER FUNCTIONS ###

    def page_validation(self, projList, appList = None):

        self.assertTrue(self.selenium.title == 'Data Science Discovery Program')

        projNameList = []
        optionList = []

        selectedProjList = [ x for x in projList if x.semester != self.short_current_semester]
        for proj in selectedProjList:
            projNameList.append(proj.project_name)

        projNameList = sorted(set(projNameList))

        # validate "Project List"
        jsonText = self.selenium.find_element_by_id("projects-json").get_attribute("text")
        projects_json = json.loads(jsonText)['projects']
        i = 0

        for project in projects_json:
            self.assertEqual(project['project_name'], projNameList[i])
            # always return non current semester even the semester is in the future
            self.assertNotEqual(project['semester'], self.current_semester)

            # validate the detail page
            project_button = self.selenium.find_element_by_id('project-'+ str(i))
            project_button.click()

            i = i + 1

            selectedProj = [x for x in selectedProjList if x.project_name == project['project_name']]

            self.assertEqual(len(selectedProj), 1)
            selectedProj = selectedProj[0]

            descr_html = BeautifulSoup(self.selenium.find_element_by_id('description').get_attribute('innerHTML'), features="html.parser")
            self.assertEqual(project['project_name'], descr_html.find("h5").text)
            self.assertEqual(project['embed_link'], descr_html.find_all('iframe')[0]['src'])

    ### END HELPER FUNCTIONS ###

    def test_access_archive_projects(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)
        partnerCt = random.randint(1, 10)
        projList = []
        appList = []
        partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('index')))
        self.page_validation (projList)

    def test_access_archive_projects_random_semester_app(self):
        projCt = random.randint(1, 10)
        appCt = random.randint(1, 10)
        partnerCt = random.randint(1, 10)
        projList = []
        appList = []
        partnerList = []

        for i in range(0, projCt):
            projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))

        for i in range(0, appCt):
            appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))

        self.selenium.get('%s%s' % (self.live_server_url, reverse('index')))
        self.page_validation (projList, appList)
