from django.test import TestCase

class AdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_name(self):
        pass
