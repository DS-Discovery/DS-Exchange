from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib.messages import get_messages

from factory_djoy import UserFactory
from user_profile.tests.factories.admin import AdminFactory
from projects.tests.factories.project import ProjectFactory
from projects.tests.factories.partner import PartnerFactory
from students.tests.factories.student import StudentFactory
from students.tests.factories.datascholar import DataScholarFactory
from applications.tests.factories.application import ApplicationFactory

class ViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.password = 'abc123'

        cls.user = UserFactory(password=cls.password)

        cls.partner = UserFactory(password=cls.password)
        cls.partner_obj = PartnerFactory(email_address=cls.partner.email)

        cls.student = UserFactory(password=cls.password)
        cls.student_obj = StudentFactory(email_address=cls.student.email)

        cls.ds_student = UserFactory(password=cls.password)
        cls.ds_obj = DataScholarFactory(email_address=cls.ds_student.email)
        cls.ds_student_obj = StudentFactory(email_address=cls.ds_student.email)

        cls.admin = AdminFactory()

        cls.project = ProjectFactory()

    def test_access_index_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_access_apply_not_logged_in(self):
        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
        response = self.client.get(reverse('apply', args=(project_name,)))
        redirect_url = f'/profile/login?next=/projects/{project_name.replace(" ", "%2520")}/apply'
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
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_apply_user_logged_in_no_profile(self):
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
        self.client.login(username=self.partner.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertEqual(response.status_code, 200)

    def test_apply_out_season_user_logged_in(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': False}]

        project_name = self.project.project_name
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
        ApplicationFactory(student=self.student_obj, project=self.project)

        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
        other_project = ProjectFactory()

        ApplicationFactory(student=self.student_obj, project=other_project)

        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (1, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
        other_project = ProjectFactory()

        ApplicationFactory(student=self.ds_student_obj, project=other_project)

        self.client.login(username=self.ds_student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (1, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project = ProjectFactory()
        project_name = project.project_name
        project.delete()

        response = self.client.get(reverse('apply', args=(project_name,)))
        self.assertEqual(response.status_code, 404)

    def test_access_admin_logged_in(self):
        self.client.login(username=self.admin.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        settings.CONSTANCE_CONFIG['APP_LIMIT'] = (10, "Number of applications any student can submit", int)
        settings.CONSTANCE_CONFIG['SCHOLAR_APP_LIMIT'] = (10, "Number of applications a Data Scholar can submit", int)
        settings.FLAGS['APPLICATIONS_OPEN'] = [{'condition': 'boolean', 'value': True}]

        project_name = self.project.project_name
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
