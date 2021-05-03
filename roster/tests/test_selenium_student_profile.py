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

# Create your tests here.
class StudentProfileTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # #default student
        # #cls.groupTypes = ['Show statuses by students', 'Show status by projects']
        # cls.groupTypes = ['student', 'project']
        # #default current Semester (config.CURRENT_SEMESTER)
        #
        # cls.short_current_semester = next(k for k,v in Project.sem_mapping.items() if v ==config.CURRENT_SEMESTER)
        # cls.semesters = [s[0] for s in Semester.choices]
        # cls.semesterCt = len(cls.semesters)
        #
        # #default ALL IN
        # cls.filters = ['Sub','Rni','Int','Rwi','Ofs','Ofr','Ofa']
        # cls.filterStates = ['IN','OUT']
        # #default 'students'
        # cls.applicantTypes = ['students', 'scholars']

        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        cls.selenium = webdriver.Chrome(r'C:\Users\eunic\Downloads\chromedriver_win32\chromedriver.exe', options=chrome_options)

        cls.logonRedirect = cls.live_server_url + "/accounts/google/login/"

        cls.input_text_name = ["first_name","last_name","student_id","major"]
        cls.input_url=["resume_link"]
        cls.input_select_name = ["college","year","python","r","sql","tableau/looker","data_visualization","data_manipulation","text-analysis","machine/deep-learning","geospatial_tools","web_development","mobile-app-development","cloud-computing","communication","self-motivation","leadership","responsibilty","teamwork","problem-solving","decisiveness","time_management","flexibility"]
        cls.input_textarea_name = ["general_question","additional_skills"]
        #cls.input_name = ['first_name':'text']

        #
        # cls.projMap = {"Project Description":"description", "Project Timeline":"timeline", "Project Workflow":"project_workflow",
        # "Dataset":"dataset", "Deliverables":"deliverable", "Additional Skills":"additional_skills", "Technical Requirements":"technical_requirements"}
        #
        # cls.projectOrganizationStr = "Project Organization: "
        #
        # cls.table_column_student= ['Student',"First_Name","Last_Name","Sub","Rni","Int","Rwi","Ofs","Ofr","Ofa","Total"]
        # cls.table_column_project= ['Project',"Contact","Sub","Rni","Int","Rwi","Ofs","Ofr","Ofa","Total"]

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

        self.selenium.get('%s%s' % (self.live_server_url,reverse('edit_student_profile')))

        self.selenium.add_cookie({'name': 'sessionid', 'value': self.client.cookies['sessionid'].value})
        self.selenium.refresh()

    def new_project_invalid_login_validation(self):
        self.selenium.find_element_by_xpath('//a[@href="newproject"]').click()

        msg_html = BeautifulSoup(self.selenium.find_element_by_id('messages').get_attribute('innerHTML'), features="html.parser")
        self.assertEqual("You must be a partner to create projects.", msg_html.find("div").text)

    def page_validation(self, student, skillset): #todo
        print(self.selenium.page_source)
        print(student)
        print(skillset)
        input ("1121")

    # def page_validation(self, groupType, semester, applicant, appList, partnerProjectList, filterArrayDict=None):
    #
    #     self.assertTrue(self.selenium.title == 'Status summary | Django site admin')
    #
    #     # TBUpdated once the filter is implemented
    #     if not filterArrayDict == None:
    #         self.assertEqual(response.context.get("filter_in_query").sort(), filterArrayDict['IN'].sort())
    #         self.assertEqual(response.context.get("filter_out_query").sort(), filterArrayDict['OUT'].sort())
    #
    #         selectedFilterSet = []
    #         for i in filterArrayDict['IN']:
    #             selectedFilterSet.append(i)
    #
    #         if len(selectedFilterSet) == 0:
    #             selectedFilterSet = self.filters.copy()
    #
    #         for i in filterArrayDict['OUT']:
    #             if i in selectedFilterSet:
    #                 selectedFilterSet.remove(i)
    #     else:
    #         selectedFilterSet = self.filters.copy()
    #
    #     selectedFilterSet = [x.upper() for x in selectedFilterSet]
    #
    #     Select(self.selenium.find_element_by_xpath("//select[@name='group']")).select_by_value(groupType)
    #     Select(self.selenium.find_element_by_xpath("//select[@name='semester']")).select_by_value(semester)
    #     Select(self.selenium.find_element_by_xpath("//select[@name='applicant']")).select_by_value(applicant)
    #     self.selenium.find_element_by_xpath("//button[@type='submit']").click()
    #
    #     table_html = BeautifulSoup(self.selenium.find_elements_by_class_name('table-container')[0].get_attribute('innerHTML'), features="html.parser")
    #
    #     table = []
    #     for row in table_html.find_all('tr'):
    #         entry = {}
    #         td_tags = row.find_all('td')
    #         i = 0
    #         for td_tag in td_tags:
    #             if (groupType == 'student') :
    #                 entry[self.table_column_student[i]] = td_tag.text
    #             else :
    #                 entry[self.table_column_project[i]] = td_tag.text
    #             i = i + 1
    #
    #         if (len(entry)) > 0:
    #             table.append(entry)
    #
    #     qualifiedAppList = []
    #     qualifiedSet = set()
    #     # compute the expected Total rows
    #     for j in appList:
    #         if j.project.semester == semester and j.status in selectedFilterSet:
    #             if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
    #                 # print(j.project.semester,j.status,j.student.email_address,j.project.project_name)
    #                 qualifiedAppList.append(j)
    #
    #     #table length remove the header row
    #     if len(qualifiedAppList) > 0:
    #         if groupType == 'student':
    #             for j in qualifiedAppList:
    #                 qualifiedSet.add(j.student.email_address)
    #
    #             # Return only applied student
    #             for i in table:
    #                 self.assertIn(i['Student'], qualifiedSet)
    #                 statusList= []
    #                 expectedRowCt = 0
    #                 for j in appList:
    #                     if j.student.email_address == i['Student'] and j.project.semester == semester:
    #                         if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
    #                             expectedRowCt = expectedRowCt + 1
    #                             statusList.append(j.status)
    #
    #                 if expectedRowCt > 0:
    #                     self.assertEqual(i['Total'], str(expectedRowCt))
    #                     for k in self.filters:
    #                         self.assertEqual(i[k], str(statusList.count(k.upper())))
    #         else: # groupType == 'project'
    #             for j in qualifiedAppList:
    #                 qualifiedSet.add(j.project.project_name)
    #
    #             for i in table:
    #                 contactList=[]
    #                 self.assertIn(i['Project'], qualifiedSet)
    #                 # check with partnerproejctList
    #                 if  not partnerProjectList == None:
    #                     for j in partnerProjectList:
    #                         if j.project.project_name == i["Project"]:
    #                             contactList.append(j.partner.email_address)
    #
    #                     if (len(contactList) == 0):
    #                         self.assertEqual("—",i['Contact'])
    #                     else:
    #                         contactList.sort()
    #                         tableContactList = i['Contact'].strip().split(", ")
    #                         tableContactList.sort()
    #                         self.assertEqual(contactList,tableContactList)
    #
    #                 statusList = []
    #                 expectedRowCt = 0
    #                 for j in appList:
    #                     if j.project.project_name == i['Project'] and j.project.semester == semester:
    #                         if (not ((applicant == 'scholars') and (not j.student.is_scholar))):
    #                             expectedRowCt = expectedRowCt + 1
    #                             statusList.append(j.status)
    #
    #                 if expectedRowCt > 0:
    #                     self.assertEqual(i['Total'], str(expectedRowCt))
    #                     for k in self.filters:
    #                         self.assertEqual(i[k], str(statusList.count(k.upper())))
    #
    #     if (len(qualifiedSet) > 0):
    #         self.assertEqual(len(table), len(qualifiedSet))

    def test_access_student_profile_no_login(self):
        self.selenium.get('%s%s' % (self.live_server_url,reverse('edit_student_profile')))
        self.assertEqual(self.logonRedirect,self.selenium.current_url)


    def test_access_student_profile_user_login(self):
        self.user_login(self.user)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_student_profile_partner_login(self):
        self.user_login(self.partner)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_student_profile_student_login(self):
        self.user_login(self.student)
        self.assertEqual(self.logonRedirect,self.selenium.current_url)

    def test_access_student_profile_admin_login(self):
        self.user_login(self.admin)
        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('edit_student_profile')))
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')


    def test_access_student_profile_edit_profile(self):
        self.user_login(self.admin)
        # TBC After authenticated, redirected to /admin ??
        # need to reload the page again for now
        self.selenium.get('%s%s' % (self.live_server_url,reverse('edit_student_profile')))
        self.assertTrue(self.selenium.find_elements_by_xpath('//h3')[0].text == 'Edit Profile')

        # student = StudentFactory()
        # #self.selenium.find_element_by_xpath('//br').send_keys('a')
        # # for item in self.input_text_name:
        # #     self.selenium.find_element_by_name(item).send_keys(student.item)
        #
        # input_text_name = ["first_name","last_name","student_id","major"]
        # self.selenium.find_element_by_name('first_name').send_keys(student.first_name)
        # self.selenium.find_element_by_name('last_name').send_keys(student.last_name)
        # self.selenium.find_element_by_name('student_id').send_keys(student.student_id)
        # self.selenium.find_element_by_name('major').send_keys(student.major)
        # self.selenium.find_element_by_name('resume_link').send_keys(student.resume_link)
        # self.selenium.find_element_by_name('general_question').send_keys(student.general_question)
        # self.selenium.find_element_by_name('additional_skills').send_keys(student.additional_skills)
        #
        # Select(self.selenium.find_element_by_name('college')).select_by_value('COE')
        # Select(self.selenium.find_element_by_name('year')).select_by_value('FA20')
        # skillset = {}
        # for skill in Student.default_skills:
        #     skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
        #     print(skillset[skill])
            #print(skill)
        # a=["Python","R","SQL","Tableau/Looker","Data Visualization","Data Manipulation","Text Analysis","Machine Learning/Deep Learning","Geospatial Data, Tools and Libraries","Web Development (frontend, backend, full stack)","Mobile App Development","Cloud Computing","communication","self-motivation","leadership","responsibility","teamwork","problem solving","decisiveness","good time management","flexibility"]

        # for i in skillset:
        #     Select(self.selenium.find_element_by_name(i)).select_by_value(skillset[i])

        # Select(self.selenium.find_element_by_name('Python')).select_by_value(skillset[skill])
        # Select(self.selenium.find_element_by_name('R')).select_by_value(skillset[skill+1])
        # Select(self.selenium.find_element_by_name('SQL')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Tableau/Looker')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Data Visualization')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Data Manipulation')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Text Analysis')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Machine Learning/Deep Learning')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Geospatial Data, Tools and Libraries')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Web Development (frontend, backend, full stack)')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Mobile App Development')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('Cloud Computing')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('communication')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('self-motivation')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('leadership')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('responsibility')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('teamwork')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('problem solving')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('decisiveness')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('good time management')).select_by_value('NE')
        # Select(self.selenium.find_element_by_name('flexibility')).select_by_value('NE')

        #self.selenium.find_element_by_xpath("//input[@type='submit']").click()
        # input("3234")


        # studentCt = random.randint(1, 10)
        # projCt = random.randint(1, 10)
        # projList = []
        # studentList = []
        # appList = []
        editList= []
        skillsetList=[]
        #
        # for i in range(0, projCt):
        #     projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
        for i in range (0,4):
            student = StudentFactory()
            input_text_name = ["first_name","last_name","student_id","major"]
            self.selenium.find_element_by_name('first_name').send_keys(student.first_name)
            self.selenium.find_element_by_name('last_name').send_keys(student.last_name)
            self.selenium.find_element_by_name('student_id').send_keys(student.student_id)
            self.selenium.find_element_by_name('major').send_keys(student.major)
            self.selenium.find_element_by_name('resume_link').send_keys(student.resume_link)
            self.selenium.find_element_by_name('general_question').send_keys(student.general_question)
            self.selenium.find_element_by_name('additional_skills').send_keys(student.additional_skills)

            Select(self.selenium.find_element_by_name('college')).select_by_value(student.college)
            Select(self.selenium.find_element_by_name('year')).select_by_value(student.year)

            skillset = {}
            for skill in Student.default_skills:
                skillset[skill] = random.choice(list(filter(None, Student.skill_levels_options.keys())))
                #print(skillset[skill])
            for i in skillset:
                Select(self.selenium.find_element_by_name(i)).select_by_value(skillset[i])

            self.selenium.find_element_by_xpath("//input[@type='submit']").click()
            editList.append(student)
            skillsetList.append(skillset)

            self.page_validation(student, skillset)

        input("2434")

        #
        # for i in range(0, studentCt):
        #     if i < studentCt//2:
        #         studentList.append(StudentFactory())
        #     else:
        #         ds = DataScholarFactory()
        #         studentList.append(StudentFactory(email_address=ds.email_address))
        #
        #     selectedProjCt = random.randint(1, projCt) - 1
        #     for projNum in random.sample(range(0, projCt), selectedProjCt):
        #         appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))
        #
        # self.user_login(self.admin)
        # self.selenium.get('%s%s' % (self.live_server_url,reverse('edit_student_profile')))
        #
        # for groupType in self.groupTypes:
        #     for semester in self.semesters:
        #         for applicant in self.applicantTypes:
        #             self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
        #             self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_random_app(self):
    #     appCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     projList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory())
    #
    #     for i in range(0, appCt):
    #         appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #     #default applicant
    #     applicant = 'students'
    #     semester = self.short_current_semester
    #     for groupType in self.groupTypes:
    #         self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #         self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_random_proj(self):
    #     studentCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     projList = []
    #     studentList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory())
    #
    #     for i in range(0, studentCt):
    #         studentList.append(StudentFactory())
    #
    #         selectedProjCt = random.randint(1, projCt) - 1
    #         for projNum in random.sample(range(0, projCt), selectedProjCt):
    #             appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     # default
    #     applicant = 'students'
    #     semester = self.short_current_semester
    #     for groupType in self.groupTypes:
    #         self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #         self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_semester(self):
    #     projCt = random.randint(1, 10)
    #     appCt = random.randint(1, 10)
    #
    #     projList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
    #
    #     for i in range(0, appCt):
    #         appList.append(ApplicationFactory(project=projList[random.randint(1, projCt) - 1]))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     # default
    #     groupType = 'student'
    #     applicant = 'students'
    #     for semester in self.semesters:
    #         self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #         self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_semester(self):
    #     studentCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     projList = []
    #     studentList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
    #
    #     for i in range(0, studentCt):
    #         studentList.append(StudentFactory())
    #         selectedProjCt = random.randint(1, projCt) - 1
    #         for projNum in random.sample(range(0, projCt), selectedProjCt):
    #             appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     #default applicant
    #     applicant = 'students'
    #     for groupType in self.groupTypes:
    #         for semester in self.semesters:
    #             self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #             self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_semester_applicant(self):
    #     studentCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     projList = []
    #     studentList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
    #
    #     for i in range(0, studentCt):
    #         if i < studentCt//2:
    #             studentList.append(StudentFactory())
    #         else:
    #             ds = DataScholarFactory()
    #             studentList.append(StudentFactory(email_address=ds.email_address))
    #
    #         selectedProjCt = random.randint(1, projCt) - 1
    #         for projNum in random.sample(range(0, projCt), selectedProjCt):
    #             appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i]))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     for groupType in self.groupTypes:
    #         for semester in self.semesters:
    #             for applicant in self.applicantTypes:
    #                 self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #                 self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_semester_applicant_random_status(self):
    #     studentCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     projList = []
    #     studentList = []
    #     appList = []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
    #
    #     for i in range(0, studentCt):
    #         if i < studentCt//2:
    #             studentList.append(StudentFactory())
    #         else:
    #             ds = DataScholarFactory()
    #             studentList.append(StudentFactory(email_address=ds.email_address))
    #
    #         selectedProjCt = random.randint(1, projCt) - 1
    #         for projNum in random.sample(range(0, projCt), selectedProjCt):
    #             appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i], status = self.filters[random.randint(1, len(self.filters)-1)].upper()))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     for groupType in self.groupTypes:
    #         for semester in self.semesters:
    #             for applicant in self.applicantTypes:
    #                 self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #                 self.page_validation(groupType, semester, applicant, appList, None)
    #
    # def test_status_summary_group_semester_applicant_partner_random_status(self):
    #     studentCt = random.randint(1, 10)
    #     projCt = random.randint(1, 10)
    #     partnerProjCt = random.randint(1, 10)
    #     projList = []
    #     studentList = []
    #     appList = []
    #     partnerProjectList= []
    #
    #     for i in range(0, projCt):
    #         projList.append(ProjectFactory(semester=self.semesters[random.randint(1, self.semesterCt)-1]))
    #
    #     for i in range(0,partnerProjCt):
    #         partnerProjectList.append(PartnerProjectInfoFactory(project=projList[random.randint(1, projCt)-1]))
    #
    #     for i in range(0, studentCt):
    #         if i < studentCt//2:
    #             studentList.append(StudentFactory())
    #         else:
    #             ds = DataScholarFactory()
    #             studentList.append(StudentFactory(email_address=ds.email_address))
    #
    #         selectedProjCt = random.randint(1, projCt) - 1
    #         for projNum in random.sample(range(0, projCt), selectedProjCt):
    #             appList.append(ApplicationFactory(project=projList[projNum], student=studentList[i], status = self.filters[random.randint(1, len(self.filters)-1)].upper()))
    #
    #     self.user_login(self.admin)
    #     self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #
    #     for groupType in self.groupTypes:
    #         for semester in self.semesters:
    #             for applicant in self.applicantTypes:
    #                 self.selenium.get('%s%s' % (self.live_server_url,reverse('admin:status_summary')))
    #                 self.page_validation(groupType, semester, applicant, appList, partnerProjectList)
