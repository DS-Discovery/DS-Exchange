import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.forms import CharField, ChoiceField, ModelForm, Select, Textarea, TextInput

from allauth.account.forms import LoginForm
from allauth.socialaccount.forms import SignupForm

from students.models import Student
from projects.models import Partner, Project

class EditProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = (
            'project_name',
            'organization',
            'project_name',
            'project_category',
            'student_num',
            'description',            
            )


class PartnerProjCreationForm(forms.ModelForm):
    field_order = [
            'email',
            'first_name',
            'last_name',
            'organization',
            'organization_description',
            'organization_website',
            'marketing_channel',
            'other_marketing_channel',
            'project_name',
            'project_category',
            'other_project_category',
            'description',
            'timeline',
            'project_workflow',
            'dataset_availability',
            'deliverable',
            'num_students',
            'other_num_students',
            'cloud_creds',
            'hce_intern',
            'optional_q1',
            'optional_q2',
            'optional_q3',
            'Python',
            'R',
            'SQL',
            'Tableau/Looker',
            'Data Visualization',
            'Data Manipulation',
            'Text Analysis',
            'Machine Learning/Deep Learning',
            'Geospatial Data, Tools and Libraries',
            'Web Development (frontend, backend, full stack)',
            'Mobile App Development',
            'Cloud Computing',
            'technical_requirements',
            'additional_skills',
            'meet_regularly',
            'survey_response',
            'environment',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for s, l in self.instance.skillset.items():
            self.fields[s] = ChoiceField(choices=Student.skill_levels, label=_(s), widget=Select(attrs={'class': 'skill-dropdown'}))
        temp_d = {
        "a": "Academia",
        "b": "Social Sector",
        "c": "Startup",
        "d": "Other",
        }
        self.fields['project_category'] = ChoiceField(choices=temp_d.items(), widget=Select(attrs={'class': 'skill-dropdown'}))
        self.order_fields(self.field_order)

    class Meta:
        model = Project
        fields = (
            # About You
            'email',
            'first_name',
            'last_name',
            'organization',
            'organization_description',
            'organization_website',
            'marketing_channel',
            'other_marketing_channel',

            # Project Details
            'project_name',
            'other_project_category',
            'description',
            'timeline',
            'project_workflow',
            'dataset_availability',
            'deliverable',
            'num_students',
            'other_num_students',
            'cloud_creds',
            'hce_intern',

            # Specification for Student Applicants
            'optional_q1',
            'optional_q2',
            'optional_q3',
            'technical_requirements',
            'additional_skills',

            # Project Partner Agreement
            'meet_regularly',
            'survey_response',
            'environment',
        )


        labels = {
            "email": "Email address",
            "marketing_channel": "How did you hear about us?",
            "other_marketing_channel": "If you chose Other, please specify here.",
            "project_name": "Project title",
            "organization": "Organization name",
            "organization_description": "About your organization",
            "project_category": "Project Sector",
            "other_project_category": "If you chose Other, describe your sector below.",
            "description": "Please provide a brief description for your project, including "
                           "the problem you hope to solve or the question you hope to answer "
                           "with the help of your Discovery team.",
            "deliverable": "What is the deliverable you hope to see from the Discovery student team? Web app, model parameters, etc.",
            "dataset_availability": "Do you have a dataset readily available?",
            "num_students": "How many student researchers (8-10 hrs/week) do you anticipate needing?",
            "other_num_students": "If you chose Other, specify the number below. We recommend onboarding 3-5 students.",
            "technical_requirements": "Please further narrow down your technical requirements, if possible, in this textbox. For example, you can use this space to specify languages "
                                 "(Swift, PHP, HTML/CSS, JS), packages/libraries (NLTK, Spacy, Pandas, Seaborn, Sklearn, OpenCV), cloud computing platforms (Azure, GCP, AWS) etc. "
                                 "Filling this out ensures that student applications match your project requirements as closely as possible.",
            "additional_skills": "Any additional qualities or skills that you would value in a student that are not mentioned in the above two questions?",
            "cloud_creds": "Would your project benefit from free cloud computing credits? Please note our current partnership is with Azure.",
            "hce_intern": "Select one:",
            "meet_regularly": "Projects are more successful when the project partner can meet regularly with the student team - "
                              "can you commit to meeting with the student team at least once a week?",
            "survey_response": "The Discovery program will regularly send out short surveys to assess the progress of projects - "
                               "can you commit to responding to all surveys?",
            "environment": "Can you commit to ensuring a safe, professional, and inclusive work environment for the students working on the project?",
            "optional_q1": "Do you have any additional questions for applicants (question 1)?",
            "optional_q2": "Do you have any additional questions for applicants (question 2)?",
            "optional_q3": "Do you have any additional questions for applicants (question 3)?",
        }
