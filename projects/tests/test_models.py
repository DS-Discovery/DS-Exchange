from django.test import TestCase
from ..models import Semester, Project, Partner, PartnerProjectInfo, Question

class ProjectTestCase(TestCase):

    # def __str__(self):
    #     return self.project_name
    #
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "project_name": self.project_name,
    #         "organization": self.organization,
    #         "embed_link": self.embed_link,
    #         "semester": self.sem_mapping[self.semester],
    #         "project_category": self.project_category.split(";") if self.project_category is not None else [],
    #         "student_num": self.student_num,
    #         "description": self.description,
    #         "questions": [q.to_dict() for q in Question.objects.filter(project=self)],
    #         "organization_description": self.organization_description,
    #         "timeline": self.timeline,
    #         "project_workflow": self.project_workflow,
    #         "dataset": self.dataset,
    #         "deliverable": self.deliverable,
    #         "skillset": self.skillset,
    #         "additional_skills": self.additional_skills,
    #         "technical_requirements": self.technical_requirements,
    #     }
    #  #

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_values = { "project_name":"Test Project Name",
                                "organization":"Test Organization",
                                "embed_link":"https://www.testproject.org",
                                "semester":"SP21",
                                "project_category":"Testing",
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
        cls.project = Project.objects.create(
            project_name=cls.project_values["project_name"],
            organization=cls.project_values["organization"],
            embed_link=cls.project_values["embed_link"],
            semester=cls.project_values["semester"],
            project_category=cls.project_values["project_category"],
            student_num=cls.project_values["student_num"],
            description=cls.project_values["description"],
            organization_description=cls.project_values["organization_description"],
            timeline=cls.project_values["timeline"],
            project_workflow=cls.project_values["project_workflow"],
            dataset=cls.project_values["dataset"],
            deliverable=cls.project_values["deliverable"],
            skillset=cls.project_values["skillset"],
            additional_skills=cls.project_values["additional_skills"],
            technical_requirements=cls.project_values["technical_requirements"]
        )

    def test_fields_as_expected(self):
        for key in self.project_values.keys():
            value = self.project_values[key]
            eval(f"self.assertEqual(self.project.{key}, {repr(value)})")

    def test_new_has_no_applicants(self):
        self.assertEqual(cls.project.num_applications(), 0)

    # def test_it_has_timestamps(self):
    #     self.assertIsInstance(self.actor.last_update, datetime)

class ModelsTestCase(TestCase):
    pass
