import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

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

    class Meta:
        model = Project
        fields = (
            # section 1
            'email',
            'first_name',
            'last_name',
            'organization',
            'organization_description',
            'organization_website',
            'marketing_channel',
            'other_marketing_channel',

            # section 2
            'project_name',
            'project_category',
            'other_project_category',
            'description',
            'timeline',
            'project_workflow',
            'dataset_availability',
            'deliverable',

            # section 3
            'num_students',
            'other_num_students',
            'skillset',
            'technical_requirements',
            'additional_skills',
            'cloud_creds',
            'hce_intern',

            # section 4
            'meet_regularly',
            'survey_response',
            'environment',

            # section 5
            'optional_q1',
            'optional_q2',
            'optional_q3',
        )

        labels = {
            "email": "Email address",
            "marketing_channel": "How did you hear about us?",
            "other_marketing_channel": "If you chose Other, please specify here.",
            "project_name": "Project title",
            "organization": "Organization name",
            "organization_description": "About your organization",
            "other_project_category": "If you chose Other, describe your category below.",
            "description": "Please provide a brief description for your project, including "
                           "the problem you hope to solve or the question you hope to answer "
                           "with the help of your Discovery team.",
            "deliverable": "What is the deliverable you hope to see from the Discovery student team? Web app, model parameters, etc.",
            "dataset_availability": "Do you have a dataset readily available?",
            "num_students": "How many student researchers (8-10 hrs/week) do you anticipate needing?",
            "other_num_students": "If you chose Other, specify the number below. We recommend onboarding 3-5 students.",
            "skillset": "Are there any specific technical skills student researchers will need to work on this project?",
            "technical_requirements": "Please further narrow down your technical requirements, if possible. For example, you can use this space to specify languages "
                                 "(Swift, PHP, HTML/CSS, JS), packages/libraries (NLTK, Spacy, Pandas, Seaborn, Sklearn, OpenCV), cloud computing platforms (Azure, GCP, AWS) etc. "
                                 "Filling this out ensures that student applications match your project requirements as closely as possible.",
            "additional_skills": "Any additional qualities or skills that you would value in a student that are not mentioned in the above two questions?",
            "cloud_creds": "Would your project benefit from availability of cloud computing credits? Please note our current partnership is with Azure.",
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