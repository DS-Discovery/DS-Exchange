from django.test import TestCase
from applications.models import Application
from students.models import Student
from projects.models import Semester, Project, Partner, PartnerProjectInfo, Question

class ProjectTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_0_categories = []
        cls.project_1_categories = ["Testing"]
        cls.project_2_categories = ["Testing", "Data Science"]

        cls.project_values_0 = {"project_name":"Test Project Name",
                                "organization":"Test Organization",
                                "embed_link":"https://www.testproject.org",
                                "semester":"SP21",
                                "project_category":";".join(cls.project_0_categories),
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
        cls.project_values_1 = {"project_name":"Test Project Name",
                                "organization":"Test Organization",
                                "embed_link":"https://www.testproject.org",
                                "semester":"SP21",
                                "project_category":";".join(cls.project_1_categories),
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
        cls.project_values_2 = {"project_name":"Test Project Name",
                                "organization":"Test Organization",
                                "embed_link":"https://www.testproject.org",
                                "semester":"SP21",
                                "project_category":";".join(cls.project_2_categories),
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

        cls.project_0 = Project.objects.create(**cls.project_values_0)
        cls.project_1 = Project.objects.create(**cls.project_values_1)
        cls.project_2 = Project.objects.create(**cls.project_values_2)

        cls.student_A = Student.objects.create(email_address="a@berkeley.edu")
        cls.student_B = Student.objects.create(email_address="b@berkeley.edu")

    def test_fields_as_expected(self):
        for key in self.project_values_0.keys():
            value = self.project_values_0[key]
            eval(f"self.assertEqual(self.project_0.{key}, {repr(value)})")

    def test_starting_applications_count(self):
        self.assertEqual(self.project_0.num_applications, 0)

    def test_applications_count_add_application(self):
        application = Application.objects.create(project=self.project_0, student_id=self.student_A.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_applications_count_remove_application(self):
        application = Application.objects.create(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        self.assertEqual(self.project_0.num_applications, 0)

    def test_applications_count_add_another_after_remove_application(self):
        application = Application.objects.create(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        application = Application.objects.create(project=self.project_0, student_id=self.student_B.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_applications_count_add_application_after_remove_for_same_student(self):
        application = Application.objects.create(project=self.project_0, student_id=self.student_A.id)
        application.delete()
        application = Application.objects.create(project=self.project_0, student_id=self.student_A.id)
        self.assertEqual(self.project_0.num_applications, 1)

    def test_string_repr_is_proj_name(self):
        self.assertEqual(str(self.project_0), self.project_values_0["project_name"])

    def test_dict_repr_starting_question_count(self):
        self.assertEqual(len(self.project_0.to_dict()['questions']), 0)

    def test_dict_repr_gets_right_questions(self):
        project_0_q_text = "project 0"
        project_1_q_text = "project 1"

        project_0_q = Question.objects.create(project=cls.project_0, question_text=project_0_q_text)
        project_1_q = Question.objects.create(project=cls.project_1, question_text=project_1_q_text)

        project_0_dict_q = self.project_0.to_dict()['questions']
        project_1_dict_q = self.project_1.to_dict()['questions']
        project_2_dict_q = self.project_2.to_dict()['questions']

        self.assertEqual(len(project_0_dict_q), 1)
        self.assertEqual(len(project_1_dict_q), 1)
        self.assertEqual(len(project_2_dict_q), 0)

        self.assertEqual(project_0_dict_q[0]['question_text'], project_0_q_text)
        self.assertEqual(project_1_dict_q[0]['question_text'], project_1_q_text)

    def test_dict_repr_no_categories(self):
        dict_repr = {
            "id": self.project_0.id,
            "project_name": self.project_0.project_name,
            "organization": self.project_0.organization,
            "embed_link": self.project_0.embed_link,
            "semester": self.project_0.sem_mapping[self.project_0.semester],
            "project_category": self.project_0_categories,
            "student_num": self.project_0.student_num,
            "description": self.project_0.description,
            "questions": [q.to_dict() for q in Question.objects.filter(project=self.project_0)],
            "organization_description": self.project_0.organization_description,
            "timeline": self.project_0.timeline,
            "project_workflow": self.project_0.project_workflow,
            "dataset": self.project_0.dataset,
            "deliverable": self.project_0.deliverable,
            "skillset": self.project_0.skillset,
            "additional_skills": self.project_0.additional_skills,
            "technical_requirements": self.project_0.technical_requirements,
        }
        proj_repr = self.project_0.to_dict()
        for key in dict_repr:
                self.assertEqual(proj_repr[key], dict_repr[key])

    def test_dict_repr_one_category(self):
        dict_repr = {
            "id": self.project_1.id,
            "project_name": self.project_1.project_name,
            "organization": self.project_1.organization,
            "embed_link": self.project_1.embed_link,
            "semester": self.project_1.sem_mapping[self.project_1.semester],
            "project_category": self.project_1_categories,
            "student_num": self.project_1.student_num,
            "description": self.project_1.description,
            "questions": [q.to_dict() for q in Question.objects.filter(project=self.project_1)],
            "organization_description": self.project_1.organization_description,
            "timeline": self.project_1.timeline,
            "project_workflow": self.project_1.project_workflow,
            "dataset": self.project_1.dataset,
            "deliverable": self.project_1.deliverable,
            "skillset": self.project_1.skillset,
            "additional_skills": self.project_1.additional_skills,
            "technical_requirements": self.project_1.technical_requirements,
        }
        proj_repr = self.project_1.to_dict()
        for key in dict_repr:
                self.assertEqual(proj_repr[key], dict_repr[key])

    def test_dict_repr_two_categories(self):
        dict_repr = {
            "id": self.project_2.id,
            "project_name": self.project_2.project_name,
            "organization": self.project_2.organization,
            "embed_link": self.project_2.embed_link,
            "semester": self.project_2.sem_mapping[self.project_2.semester],
            "project_category": self.project_2_categories,
            "student_num": self.project_2.student_num,
            "description": self.project_2.description,
            "questions": [q.to_dict() for q in Question.objects.filter(project=self.project_2)],
            "organization_description": self.project_2.organization_description,
            "timeline": self.project_2.timeline,
            "project_workflow": self.project_2.project_workflow,
            "dataset": self.project_2.dataset,
            "deliverable": self.project_2.deliverable,
            "skillset": self.project_2.skillset,
            "additional_skills": self.project_2.additional_skills,
            "technical_requirements": self.project_2.technical_requirements,
        }
        proj_repr = self.project_2.to_dict()
        for key in dict_repr:
                self.assertEqual(proj_repr[key], dict_repr[key])

class PartnerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_0_info = {
        "email_address":"ab@berkeley.edu",
        "first_name":"a",
        "last_name":"b"
        }
        cls.partner_1_info = {
        "email_address":"cd@berkeley.edu",
        "first_name":"c",
        "last_name":"d"
        }
        cls.partner_2_info = {
        "email_address":"ef@berkeley.edu",
        "first_name":"e",
        "last_name":"f"
        }
        cls.partner_0 = Partner.objects.create(**cls.partner_0_info)
        cls.partner_1 = Partner.objects.create(**cls.partner_1_info)
        cls.partner_2 = Partner.objects.create(**cls.partner_2_info)

    def test_string_repr_is_email_address(self):
        self.assertEqual(str(self.partner_0), self.partner_0_info["email_address"])

    def test_fields_as_expected(self):
        for key in self.partner_0_info.keys():
            value = self.partner_0_info[key]
            eval(f"self.assertEqual(self.partner_0.{key}, {repr(value)})")

    def test_starting_projects_count(self):
        self.assertEqual(self.partner_0.projects.count(), 0)

    def test_projects_count_add_project(self):
        project_0 = Project.objects.create()

        self.assertEqual(self.partner_0.projects.count(), 0)
        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        self.partner_0.projects.add(project_0)

        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

        project_1 = Project.objects.create()

        self.partner.partner_1.add(project_1)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 1)
        self.assertEqual(self.partner_1.projects.get(id=project_1.id), project_1)

        self.assertEqual(self.partner_2.projects.count(), 0)

    def test_projects_with_multiple_partners(self):
        project_0 = Project.objects.create()

        self.partner_0.projects.add(project_0)
        self.partner_1.projects.add(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 1)
        self.assertEqual(self.partner_1.projects.get(id=project_1.id), project_0)
        self.assertEqual(self.partner_2.projects.count(), 0)

        project_1 = Project.objects.create()

        self.partner.partner_1.add(project_1)
        self.partner.partner_2.add(project_1)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.count(), 2)
        self.assertEqual(self.partner_1.projects.get(id=project_0.id), project_0)
        self.assertEqual(self.partner_1.projects.get(id=project_1.id), project_1)
        self.assertEqual(self.partner_2.projects.count(), 1)
        self.assertEqual(self.partner_2.projects.get(id=project_1.id), project_1)


    def test_projects_count_remove_project(self):
        project_0 = Project.objects.create()

        self.partner_0.projects.add(project_0)
        self.partner_1.projects.add(project_0)
        self.partner_1.projects.remove(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

        self.assertEqual(self.partner_1.projects.count(), 0)
        self.assertEqual(self.partner_2.projects.count(), 0)


    def test_projects_count_add_another_after_remove_project(self):
        project_0 = Project.objects.create()

        self.partner_0.projects.add(project_0)
        self.partner_0.projects.remove(project_0)
        self.partner_0.projects.add(project_0)

        self.assertEqual(self.partner_0.projects.count(), 1)
        self.assertEqual(self.partner_0.projects.get(id=project_0.id), project_0)

class PartnerProjectInfoTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_info = {
        "email_address":"ab@berkeley.edu",
        "first_name":"a",
        "last_name":"b"
        }
        cls.project_info = {
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

        cls.partner = Partner.objects.create(**cls.partner_info)
        cls.project = Project.objects.create(**cls.project_info)

        cls.partner_project_info = {
        "partner": cls.partner,
        "project": cls.project,
        "role": "Manager"
        }

        cls.partner_project = PartnerProjectInfo.objects.create(**cls.partner_project_info)

    def test_string_repr_is_partner_project(self):
        self.assertEqual(str(self.partner_0), f"{self.partner_project_info.partner}+{self.partner_project_info.project}")

    def test_fields_as_expected(self):
        for key in self.partner_project_info.keys():
            value = self.partner_project[key]
            eval(f"self.assertEqual(self.partner_project_info.{key}, {repr(value)})")



class QuestionTestCase(TestCase):
    # class Question(models.Model):
    #     project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #     question_text = models.CharField(max_length=200)
    #     question_type = models.CharField(max_length=50, choices=question_choices, default='text')
    #     question_data =  models.CharField(max_length=1000, null=True, blank=True)
    #
    #     def to_dict(self):
    #         return {
    #             "id": self.id,
    #             "project": self.project.id,
    #             "question_text": self.question_text,
    #             "question_type": self.question_type,
    #             "question_data": self.question_data,
    #         }
    #
    #     def __str__(self):
    #         return self.project.project_name + " - " + self.question_text

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_info = {
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

        cls.project = Project.objects.create(**cls.project_info)

        cls.question_info = {
        "project": cls.project,
        "question_text": "Example question",
        "question_type": "text"
        }

        cls.question = Question.objects.create(**cls.question_info)

    def test_string_repr_is_project_question(self):
        self.assertEqual(str(self.question), f"{self.question.project.project_name} - {self.question.question_text}")

    # def test_fields_as_expected(self):
    #     for key in self.partner_project_info.keys():
    #         value = self.partner_project[key]
    #         eval(f"self.assertEqual(self.partner_project_info.{key}, {repr(value)})")
