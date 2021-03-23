from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from projects.models import Project, Partner
from students.models import Student, DataScholar
from applications.models import Application

class ViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_values = {
        "username":"john",
        "email":"jdoe@email.com",
        "password":"password"
        }
        cls.partner_values = {
        "username":"jake",
        "email":"jbdoe@email.com",
        "password":"password"
        }
        cls.student_values = {
        "username":"jane",
        "email":"jjdoe@email.com",
        "password":"password"
        }
        cls.ds_student_values = {
        "username":"data",
        "email":"ds@email.com",
        "password":"password"
        }
        cls.admin_values = {
        "username":"admin",
        "email":"admin@email.com",
        "password":"big admin"
        }
        cls.project_values = {"project_name":"Test Project Name",
                              "organization":"Test Organization",
                              "embed_link":"https://www.testproject.org",
                              "semester":"SP21",
                              "project_category":"",
                              "student_num":10,
                              "description":"This is the description of a test project.",
                              "organization_description":"This is the description of the test organization.",
                              "timeline":"Soon...",
                              "project_workflow":"We use Agile.",
                              "dataset":"Photographs provided by the MET.",
                              "deliverable":"Computer vision algorithm to identify time periods.",
                              "skillset":"{'test skill A':'yes', 'test skill B':'ideally...'}",
                              "additional_skills":"Positive attitude is a MUST.",
                              "technical_requirements":"ML background." }

        cls.user = User.objects.create_user(**cls.user_values)
        cls.partner = User.objects.create_user(**cls.partner_values)
        cls.partner_obj = Partner.objects.create(email_address=cls.partner_values['email'])
        cls.student = User.objects.create_user(**cls.student_values)
        cls.student_obj = Student.objects.create(email_address=cls.student_values['email'])
        cls.ds_student = User.objects.create_user(**cls.ds_student_values)
        cls.ds_obj = DataScholar.objects.create(email_address=cls.ds_student_values['email'])
        cls.ds_student_obj = Student.objects.create(email_address=cls.ds_student_values['email'])
        cls.admin = User.objects.create_superuser(**cls.admin_values)
        cls.project = Project.objects.create(**cls.project_values)

    def test_access_index_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_access_apply_not_logged_in(self):
        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        redirect_url = '/profile/login?next=/projects/Test%2520Project%2520Name/apply'
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=302,
                             fetch_redirect_response=True)

        response = self.client.get(redirect_url)
        auth_url = '/accounts/google/login'
        self.assertRedirects(response,
                             auth_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=False)

    def test_access_user_logged_in(self):
        self.client.login(username=self.user_values['username'], password=self.user_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_apply_user_logged_in_no_profile(self):
        self.client.login(username=self.user_values['username'], password=self.user_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/profile/signup',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You have not yet signed up. Please complete the signup form to continue.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_apply_in_season_partner_logged_in(self):
        self.client.login(username=self.partner_values['username'], password=self.partner_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/projects',
                             status_code=302,
                             target_status_code=301,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You must be a student to apply to projects.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_apply_in_season_student_logged_in(self):
        self.client.login(username=self.student_values['username'], password=self.student_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertEqual(response.status_code, 200)

    def test_apply_out_season_user_logged_in(self):
        self.client.login(username=self.student_values['username'], password=self.student_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': False}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        proj_url = '/projects'
        self.assertRedirects(response,
                             proj_url,
                             status_code=302,
                             target_status_code=301,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'Applications are currently closed. If you believe you have received this message in error, please email ds-discovery@berkeley.edu.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_already_applied(self):
        Application.objects.create(
        student=self.student_obj,
        project=self.project
        )

        self.client.login(username=self.student_values['username'], password=self.student_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/projects',
                             status_code=302,
                             target_status_code=301,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You have already applied to this project.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_max_applications_student(self):
        other_proj_name = "Other Project"
        other_project = Project.objects.create(project_name=other_proj_name)

        Application.objects.create(
        student=self.student_obj,
        project=other_project
        )

        self.client.login(username=self.student_values['username'], password=self.student_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (1, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/projects',
                             status_code=302,
                             target_status_code=301,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You have already applied to 1 projects.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_max_applications_data_scholar(self):
        other_proj_name = "Other Project"
        other_project = Project.objects.create(project_name=other_proj_name)

        Application.objects.create(
        student=self.ds_student_obj,
        project=other_project
        )

        self.client.login(username=self.ds_student_values['username'], password=self.ds_student_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (1, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/projects',
                             status_code=302,
                             target_status_code=301,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You have already applied to 1 projects.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_nonexistent_project(self):
        self.client.login(username=self.user_values['username'], password=self.user_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = "i dont exist"

        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertEqual(response.status_code, 404)

    def test_access_admin_logged_in(self):
        self.client.login(username=self.admin_values['username'], password=self.admin_values['password'])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]
        project_name = self.project_values["project_name"]
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertRedirects(response,
                             '/profile/signup',
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        messages = list(get_messages(response.wsgi_request))
        message = 'You have not yet signed up. Please complete the signup form to continue.'
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)
