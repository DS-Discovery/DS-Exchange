from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from constance import config
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
        cls.logon_redirect = "/profile/login?next=/profile/"

    def test_access_not_logged_in(self):
        response = self.client.get(reverse('get_profile'))
        self.assertRedirects(response,
                             self.logon_redirect,
                             status_code=302,
                             fetch_redirect_response=False)

    def test_logged_in_no_profile(self):
        self.client.login(username=self.user.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.get(reverse('get_profile'))
        self.assertRedirects(response,
                             reverse('student_signup'),
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_student_logged_in_with_profile(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.get(reverse('get_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/student_profile.html')

    def test_partner_logged_in_with_profile(self):
        self.client.login(username=self.partner.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.get(reverse('get_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/partner_profile.html')

    def test_edit_profile_out_of_season(self):
        self.client.login(username=self.student.username, password=self.password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        config.APPLICATIONS_OPEN = False
        response = self.client.get(reverse('edit_student_profile'))
        self.assertRedirects(response,
                             reverse('get_profile'),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True
                            )
        messages = list(get_messages(response.wsgi_request))
        message = 'Applications are currently closed and applicants are not longer allowed to edit their profiles. If you believe you have received this message in error, please email ds-discovery@berkeley.edu.'
        self.assertEqual(str(messages[0]), message)
