from django.test import TestCase

from applications.models import Answer
from applications.tests.factories.application import ApplicationFactory
from applications.tests.factories.answer import AnswerFactory
from students.tests.factories.student import StudentFactory
from projects.tests.factories.project import ProjectFactory
from projects.tests.factories.question import QuestionFactory

from datetime import datetime

class ApplicationModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_0_categories = []
        cls.project_1_categories = ["Testing"]

        cls.project_0 = ProjectFactory(project_category = ';'.join(cls.project_0_categories))
        cls.project_1 = ProjectFactory(project_category = ';'.join(cls.project_1_categories))

        cls.student_A = StudentFactory()
        cls.student_B = StudentFactory()

        cls.application_1 = ApplicationFactory(project=cls.project_0, student_id=cls.student_A.id)
        cls.application_2 = ApplicationFactory(project=cls.project_1, student_id=cls.student_B.id)

    def test_has_timestamp(self):
        self.assertIsInstance(self.application_1.created_at, datetime)

    def test_has_rank(self):
        self.assertIsInstance(self.application_1.rank, int)

    def test_has_status(self):
        self.assertIsInstance(self.application_1.status, str)

    def test_student_field(self):
        self.assertEqual(self.application_1.student, self.student_A)
        self.assertEqual(self.application_2.student, self.student_B)

    def test_project_field(self):
        self.assertEqual(self.application_1.project, self.project_0)
        self.assertEqual(self.application_2.project, self.project_1)

    def test_status_field(self):
        self.assertEqual(self.application_1.status, "SUB")
        self.assertEqual(self.application_2.status, "SUB")

    def test_dict_repr(self):
        dict_repr = {
            "student": self.application_1.student.id,
            "project": self.application_1.project.id,
            "created_at": str(self.application_1.created_at),
            "rank": self.application_1.rank,
            "status": self.application_1.status,
            "answers": [a.to_dict() for a in Answer.objects.filter(application=self.application_1)],
            "app_status_choices": self.application_1.app_status_choices,
        }
        application_repr = self.application_1.to_dict()
        for key in application_repr:
                self.assertEqual(application_repr[key], dict_repr[key])

    def test_string_repr_is(self):
        self.assertEqual(str(self.application_1), f"{self.application_1.student.email_address} application for {self.application_1.project.project_name}")

class AnswerModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.answer = AnswerFactory()

    def test_string_repr(self):
        self.assertEqual(str(self.answer), self.answer.answer_text)

    def test_dict_repr(self):
        dict_repr = {
            "student": self.answer.student.id,
            "application": self.answer.application.id,
            "question": self.answer.question.id,
            "answer_text": self.answer.answer_text,
        }
        answer_repr = self.answer.to_dict()
        for key in answer_repr:
                self.assertEqual(answer_repr[key], dict_repr[key])
