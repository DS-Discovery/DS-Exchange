from django.test import TestCase

from projects.models import Semester, Question

from applications.tests.factories.application import ApplicationFactory
from students.tests.factories.student import StudentFactory
from projects.tests.factories.project import ProjectFactory
from projects.tests.factories.partner import PartnerFactory
from projects.tests.factories.partnerprojectinfo import PartnerProjectInfoFactory
from projects.tests.factories.question import QuestionFactory

class ProjectTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_0_categories = []
        cls.project_1_categories = ["Testing"]
        cls.project_2_categories = ["Testing", "Data Science"]

        cls.project_0 = ProjectFactory(project_category = ';'.join(cls.project_0_categories))
        cls.project_1 = ProjectFactory(project_category = ';'.join(cls.project_1_categories))
        cls.project_2 = ProjectFactory(project_category = ';'.join(cls.project_2_categories))

        cls.student_A = StudentFactory()
        cls.student_B = StudentFactory()

    def test_starting_applications_count(self):
        self.assertEqual(self.project_0.num_applications, 0)

    def test_applications_count_add_application(self):
        application = ApplicationFactory(project=self.project_0, student_id=self.student_A.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_applications_count_remove_application(self):
        application = ApplicationFactory(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        self.assertEqual(self.project_0.num_applications, 0)

    def test_applications_count_add_another_after_remove_application(self):
        application = ApplicationFactory(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        application = ApplicationFactory(project=self.project_0, student_id=self.student_B.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_applications_count_add_application_after_remove_for_same_student(self):
        application = ApplicationFactory(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        application = ApplicationFactory(project=self.project_0, student_id=self.student_A.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_string_repr_is_proj_name(self):
        self.assertEqual(str(self.project_0), self.project_0.project_name)

    def test_dict_repr_starting_question_count(self):
        self.assertEqual(len(self.project_0.to_dict()['questions']), 0)

    def test_dict_repr_gets_right_questions(self):
        project_0_q = QuestionFactory(project=self.project_0)
        project_1_q = QuestionFactory(project=self.project_1)

        project_0_dict_q = self.project_0.to_dict()['questions']
        project_1_dict_q = self.project_1.to_dict()['questions']
        project_2_dict_q = self.project_2.to_dict()['questions']

        self.assertEqual(len(project_0_dict_q), 1)
        self.assertEqual(len(project_1_dict_q), 1)
        self.assertEqual(len(project_2_dict_q), 0)

        self.assertEqual(project_0_dict_q[0]['question_text'], project_0_q.question_text)
        self.assertEqual(project_1_dict_q[0]['question_text'], project_1_q.question_text)

    def test_dict_repr_no_categories(self):
        proj_repr = self.project_0.to_dict()
        dict_repr = {}
        for key in proj_repr.keys():
            val = None
            if key == "semester":
                val = self.project_0.sem_mapping[self.project_0.semester]
            elif key == "project_category":
                val = self.project_0_categories
            elif key == "questions":
                val = [q.to_dict() for q in Question.objects.filter(project=self.project_0)]
            else:
                val = eval(f'self.project_0.{key}')
            dict_repr[key] = val
        for key in dict_repr:
                self.assertEqual(proj_repr[key], dict_repr[key])

    def test_dict_repr_one_category(self):
        proj_repr = self.project_1.to_dict()
        dict_repr = {}
        for key in proj_repr.keys():
            val = None
            if key == "semester":
                val = self.project_1.sem_mapping[self.project_1.semester]
            elif key == "project_category":
                val = self.project_1_categories
            elif key == "questions":
                val = [q.to_dict() for q in Question.objects.filter(project=self.project_1)]
            else:
                val = eval(f'self.project_1.{key}')
            dict_repr[key] = val
        for key in dict_repr:
                self.assertEqual(proj_repr[key], dict_repr[key])

    def test_dict_repr_two_categories(self):
        proj_repr = self.project_2.to_dict()
        dict_repr = {}
        for key in proj_repr.keys():
            val = None
            if key == "semester":
                val = self.project_2.sem_mapping[self.project_2.semester]
            elif key == "project_category":
                val = self.project_2_categories
            elif key == "questions":
                val = [q.to_dict() for q in Question.objects.filter(project=self.project_2)]
            else:
                val = eval(f'self.project_2.{key}')
            dict_repr[key] = val
        for key in dict_repr:
            self.assertEqual(proj_repr[key], dict_repr[key])


class PartnerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_0 = PartnerFactory()
        cls.partner_1 = PartnerFactory()
        cls.partner_2 = PartnerFactory()

    def test_string_repr_is_email_address(self):
        self.assertEqual(str(self.partner_0), self.partner_0.email_address)

    def test_starting_projects_count(self):
        self.assertEqual(self.partner_0.projects.count(), 0)

    def test_projects_count_add_project(self):
        project_0 = ProjectFactory()
        self.assertEqual(self.partner_0.projects.count(), 0)
        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        self.partner_0.projects.add(project_0)

        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

        project_1 = ProjectFactory()

        self.partner_1.projects.add(project_1)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 1)
        self.assertEqual(self.partner_1.projects.get(id=project_1.id), project_1)

        self.assertEqual(self.partner_2.projects.count(), 0)

    def test_projects_with_multiple_partners(self):
        project_0 = ProjectFactory()

        self.partner_0.projects.add(project_0)
        self.partner_1.projects.add(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 1)
        self.assertEqual(self.partner_1.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        project_1 = ProjectFactory()

        self.partner_1.projects.add(project_1)
        self.partner_2.projects.add(project_1)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 2)
        self.assertEqual(self.partner_1.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.get(id=project_1.id), project_1)
        self.assertEqual(self.partner_2.projects.count(), 1)
        self.assertEqual(self.partner_2.projects.get(id=project_1.id), project_1)


    def test_projects_count_remove_project(self):
        project_0 = ProjectFactory()

        self.partner_0.projects.add(project_0)
        self.partner_1.projects.add(project_0)
        self.partner_1.projects.remove(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)

    def test_projects_count_add_again_after_remove_project(self):
        project_0 = ProjectFactory()

        self.partner_0.projects.add(project_0)
        self.partner_0.projects.remove(project_0)
        self.partner_0.projects.add(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

    def test_projects_count_add_new_after_remove_project(self):
        project_0 = ProjectFactory()

        self.partner_0.projects.add(project_0)
        self.partner_0.projects.remove(project_0)

        project_1 = ProjectFactory()

        self.partner_0.projects.add(project_1)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_1.id), project_1)


class PartnerProjectInfoTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_values = {
        "email_address":"ab@berkeley.edu",
        "first_name":"a",
        "last_name":"b"
        }
        cls.project_values = {
        "project_name":"Test Project Name",
        "organization":"Test Organization",
        "embed_link":"https://www.testproject.org",
        "semester":"SP21",
        "project_category":[],
        "student_num":10,
        "description":"This is the description of a test project.",
        "organization_description":"This is the description of the test organization.",
        "timeline":"Soon...",
        "project_workflow":"We use Agile.",
        "dataset":"Photographs provided by the MET.",
        "deliverable":"Computer vision algorithm to identify time periods.",
        "skillset":"{'test skill A':'yes', 'test skill B':'ideally...'}",
        "additional_skills":"Positive attitude is a MUST.",
        "technical_requirements":"ML background."
        }

        cls.partner = PartnerFactory()
        cls.project = ProjectFactory()

        cls.partner_project_values = {
        "partner": cls.partner,
        "project": cls.project,
        "role": "Manager"
        }

        cls.partner_project = PartnerProjectInfoFactory(partner=cls.partner, project=cls.project)

    def test_string_repr_is_partner_project(self):
        self.assertEqual(str(self.partner_project), f"{self.partner_project.partner}+{self.partner_project.project}")


class QuestionTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = ProjectFactory()
        cls.question = QuestionFactory(project=cls.project)

    def test_string_repr_is_project_question(self):
        self.assertEqual(str(self.question), f"{self.question.project.project_name} - {self.question.question_text}")

    def test_dict_repr_no_categories(self):
        dict_repr = {
        "id": self.question.id,
        "project": self.question.project.id,
        "question_text": self.question.question_text,
        "question_type": self.question.question_type,
        "question_data": self.question.question_data,
        }
        question_repr = self.question.to_dict()
        for key in question_repr:
                self.assertEqual(question_repr[key], dict_repr[key])
