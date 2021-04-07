from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.messages import get_messages

from factory_djoy import UserFactory
from projects.tests.factories.project import ProjectFactory
from projects.tests.factories.partner import PartnerFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory
from students.tests.factories.student import StudentFactory
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

        cls.project = ProjectFactory()

    def test_access_display_not_logged_in(self):
        response = self.client.get(reverse('display_student_team_roster'))
        redirect_url = f'/profile/login?next=/roster/'
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

    def test_access_display_student_logged_in_not_member(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('display_student_team_roster'))
        self.assertRedirects(response,
             '/projects',
             status_code=302,
             target_status_code=301,
             fetch_redirect_response=True)

        messages = list(get_messages(response.wsgi_request))
        message="You must be a member of a project team to view the roster."

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_display_student_logged_in_not_auth(self):
        self.client.login(username=self.student.username, password="")
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated==False)

    def test_access_display_student_logged_in_not_member(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('display_student_team_roster'))
        self.assertRedirects(response,
             '/projects',
             status_code=302,
             target_status_code=301,
             fetch_redirect_response=True)

        messages = list(get_messages(response.wsgi_request))
        message="You must be a member of a project team to view the roster."

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_display_student_logged_in_member_without_OFA_proj(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        ApplicationFactory(student=self.student_obj, project=self.project,status = "SUB")

        response = self.client.get(reverse('display_student_team_roster'))
        self.assertRedirects(response,
             '/projects',
             status_code=302,
             target_status_code=301,
             fetch_redirect_response=True)

        messages = list(get_messages(response.wsgi_request))
        message="You must be a member of a project team to view the roster."

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_display_partner_logged_in(self):
        self.client.login(username=self.partner.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('display_student_team_roster'))
        self.assertRedirects(response,
             '/applications',
             status_code=302,
             target_status_code=301,
             fetch_redirect_response=True)

        messages = list(get_messages(response.wsgi_request))
        message="Partners view the roster in applications."

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_display_user_logged_in(self):
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('display_student_team_roster'))
        self.assertRedirects(response,
             '/',
             status_code=302,
             target_status_code=200,
             fetch_redirect_response=True)

        messages = list(get_messages(response.wsgi_request))
        message="You must be a member of a project team to view the roster."

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_access_display_student_logged_in_member_with_OFA_proj(self):
            self.client.login(username=self.student.username, password=self.password)
            user = auth.get_user(self.client)
            self.assertTrue(user.is_authenticated)

            partner_proj = PartnerProjectInfoFactory(project=self.project,partner=self.partner_obj)
            ApplicationFactory(student=self.student_obj, project=self.project,status = "OFA")

            response = self.client.get(reverse('display_student_team_roster'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context.get('students').count(), 1)
            self.assertEqual(response.context.get('students')[0].email_address, self.student.email)
            self.assertEqual(response.context.get('project'), self.project)
            self.assertEqual(response.context.get('projectPartners').count(), 1)
            self.assertEqual(response.context.get('projectPartners')[0], partner_proj)
