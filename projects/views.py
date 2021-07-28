import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, Http404, render, redirect
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from constance import config

from applications.forms import AnswerForm
from applications.models import Answer, Application
from students.models import Student

from .forms import EditProjectForm
from .forms import PartnerProjCreationForm
from .models import Partner, PartnerProjectInfo, Project, Question, get_default_skills
from django.http import HttpResponse

logger = logging.getLogger(__name__)


# @login_required
def list_projects(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email

    # if email is None:
    #     return redirect('/profile/login')

    projects_json = get_projects_json()
    for i, project in list(enumerate(projects_json['projects']))[::-1]:
        if Application.objects.filter(project_id=project['id']).count() >= config.HIDE_PROJECT_APPLICATION_THRESHOLD:
            projects_json['projects'].pop(i)

    context = {
        "projects_json": projects_json,
        "selected": request.GET.get('selected', ''),
        "selected": request.GET.get('selected', ''),
        "is_partner": Partner.objects.filter(email_address=email).count() > 0,
        "is_student": Student.objects.filter(email_address=email).count() > 0,
    }

    return render(request, 'projects/listing.html', context)


def get_projects_json():
    projects = []
    for p in Project.objects.all():
        d = p.to_dict()
        if d['semester'] == config.CURRENT_SEMESTER:
            d["num_applicants"] = Application.objects.filter(project=p).count()
            projects.append(d)

    projects = sorted(projects, key=lambda d: d["project_name"])

    return {"projects": projects}


@login_required
def apply(request, project_name):
    # this view shows the project name as well as the project questions
    # need to add user authentication

    # check to see if that partner project exists, if so, get the questions for it
    try:
        project = Project.objects.get(project_name=project_name)
        questions = Question.objects.filter(project=project)  # .order_by('question_num')
    except Question.DoesNotExist:
        raise Http404("Question does not exist.")
    except Project.DoesNotExist:
        raise Http404("Project does not exist.")

    email = None
    if request.user.is_authenticated:
        email = request.user.email
    else:
        messages.info(request, "You must be logged in to apply to a project.")
        return redirect('/')

    try:
        student = Student.objects.get(email_address=email)
    except ObjectDoesNotExist:
        if Partner.objects.filter(email_address=email).count() > 0:
            messages.info(request, "You must be a student to apply to projects.")
            return redirect("/projects")
        else:
            messages.info(request, "You have not yet signed up. Please complete the signup form to continue.")
            return redirect("/profile/signup")

    if not config.APPLICATIONS_OPEN:
        messages.info(
            request,
            "Applications are currently closed. If you believe you have received "
            "this message in error, please email ds-discovery@berkeley.edu."
        )
        return redirect("/projects")

    count = Application.objects.filter(student=student).count()

    if count > config.APP_LIMIT - 1 and not student.is_scholar:
        messages.info(request, f'You have already applied to {config.APP_LIMIT} projects.')
        return redirect('/projects')
    elif count > config.SCHOLAR_APP_LIMIT - 1 and student.is_scholar:
        messages.info(request, f'You have already applied to {config.SCHOLAR_APP_LIMIT} projects.')
        return redirect('/projects')

    count = Application.objects.filter(student=student, project=project).count()

    if count > 0:
        # raise Http404("Student already has an application submitted")
        messages.info(request, 'You have already applied to this project.')
        return redirect('/projects')

    # if this form is submitted, then we want to save the answers
    if request.method == 'POST':

        post = request.POST.copy()

        def querydict_to_dict(query_dict):
            data = {}
            for key in query_dict.keys():
                v = query_dict.getlist(key)
                if len(v) == 1:
                    v = v[0]
                data[key] = v
            return data

        is_valid = True
        question_ids = list(post.keys())

        ans_list = []
        # creating individual answers
        for q_id in question_ids:
            if q_id == "csrfmiddlewaretoken":
                continue

            if len(post[q_id].strip()) == 0:
                is_valid = False
                break

            new_ans = request.POST.copy()
            new_ans_keys = list(new_ans.keys())
            q_num = 0
            answer_text = ""
            for new_k in new_ans_keys:
                if new_k == "csrfmiddlewaretoken":
                    continue
                if new_k == q_id:
                    q_num = new_k
                    # answer_text = post[new_k]
                    asDict = querydict_to_dict(post)
                    if type(asDict[q_id]) != list:
                        answer_text = asDict[q_id]
                    else:
                        answer_text = ";".join(asDict[q_id])

                new_ans.pop(new_k)

            new_ans['question'] = Question.objects.get(id=q_num)
            new_ans['answer_text'] = answer_text
            ans_list.append(new_ans)

        # print(ans_list)
        for skill in get_default_skills():
            if (skill not in student.skills.keys()) or (not student.skills[skill]):
                messages.info(
                    request,
                    'Please ensure you have filled out your skill levels in your profile.'
                )
                return redirect(request.path_info)

        if is_valid:

            try:
                application = Application.objects.get(student=student, project=project)
            except:
                application = Application(student=student, project=project, status="SUB")

            application.save()

            answers = []
            for post in ans_list:
                # print(post)

                request.POST = post

                form = AnswerForm(request.POST)

                if form.is_valid():
                    # print("Is valid")

                    question = form.cleaned_data['question']

                    try:
                        a = Answer.objects.get(student=student, application=application, question=question)
                        a.answer_text = form.cleaned_data['answer_text']

                    except:
                        a = Answer(student=student, application = application, question = question, answer_text = form.cleaned_data['answer_text'])

                    a.save()
                    answers.append(a)

                else:
                    # cleanup on failure
                    application.delete()
                    for a in answers:
                        a.delete()

                    logger.error(f"Invalid answer for application {application}:\n{form}")
                    messages.info(
                        request,
                        'Your application was invalid and could not be processed. If this error persists, '
                        'please contact ds-discovery@berkeley.edu.'
                    )
                    return redirect('/projects')

            # TODO: allow students to update rank
            # studentUpdater = Student.objects.filter(email_address = email)
            # if not student.first_choice:
            #     studentUpdater.update(first_choice = project.project_name)
            # elif not student.second_choice:
            #     studentUpdater.update(second_choice = project.project_name)
            # elif not student.third_choice:
            #     studentUpdater.update(third_choice = project.project_name)
            # else:
            #     # raise Http404("Student has applied to 3 applications")
            #     messages.info(request, 'You have already applied to 3 projects.')
            #     return redirect('/projects')

            # application.save()
            send_app_confirmation_email(application)

            messages.info(request, 'Your application has been submitted successfully!')
            return redirect('/projects')

        else:
            messages.info(
                request,
                'Your application was invalid and could not be processed. If this error persists, '
                'please contact ds-discovery@berkeley.edu.'
            )
            return redirect(request.path_info)
    else: # GET
        form = AnswerForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    # print(project, type(project))
    # print(questions)

    if request.user.is_authenticated:
        print(questions)
        return render(request, 'projects/application.html', {'questions': questions, 'project': project, 'form': form})
    else:
        raise PermissionDenied("User is not logged in.")


def send_app_confirmation_email(app):
    html_message = render_to_string("emails/app_confirmation.html", {"project": app.project})
    plain_message = strip_tags(html_message)

    send_mail(
        "DS Discovery Application Confirmation",
        plain_message,
        settings.EMAIL_HOST_USER,
        [app.student.email_address],
        html_message=html_message,
    )

    print(f"Sent confirmation email to {app.student.email_address}")

@login_required
def proj_creation(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    if Partner.objects.filter(email_address=email).count() == 0:
        messages.info(request, "You must be a partner to create projects.")
        return redirect("/projects")
    if request.method == 'POST':
        form = PartnerProjCreationForm(request.POST)
        if form.is_valid():
            skills_and_levels = {
                "Python": form.cleaned_data["Python"],
                "R": form.cleaned_data["R"],
                "SQL": form.cleaned_data["SQL"],
                "Tableau/Looker": form.cleaned_data["Tableau/Looker"],
                "Data Visualization": form.cleaned_data["Data Visualization"],
                "Data Manipulation": form.cleaned_data["Data Manipulation"],
                "Text Analysis": form.cleaned_data["Text Analysis"],
                "Machine Learning/Deep Learning": form.cleaned_data["Machine Learning/Deep Learning"],
                "Geospatial Data, Tools and Libraries": form.cleaned_data["Geospatial Data, Tools and Libraries"],
                "Web Development (frontend, backend, full stack)": form.cleaned_data["Web Development (frontend, backend, full stack)"],
                "Mobile App Development": form.cleaned_data["Mobile App Development"],
                "Cloud Computing": form.cleaned_data["Cloud Computing"],
            }
            for i in skills_and_levels.keys():
                if skills_and_levels[i] == 'FA':
                    skills_and_levels[i] = 'Familiar'
                elif skills_and_levels[i] == 'BE':
                    skills_and_levels[i] = 'Beginner'
                elif skills_and_levels[i] == 'IN':
                    skills_and_levels[i] = 'Intermediate'
                elif skills_and_levels[i] == 'AD':
                    skills_and_levels[i] = 'Advanced'
                elif skills_and_levels[i] == 'NE':
                    skills_and_levels[i] = 'No Experience'
                else:
                    continue
            # TODO: Project creation hardcoded semester, it seems. Replace with env var (discovery/settings).
            proj = Project(email = form.cleaned_data['email'] if form.cleaned_data['email'] else email,
                          organization=form.cleaned_data['organization'],
                          project_name=form.cleaned_data['project_name'],
                          project_category=form.cleaned_data['project_sector'],
                          description=form.cleaned_data['description'],
                          semester="FA21",
                          organization_description=form.cleaned_data['organization_description'],
                          other_marketing_channel=form.cleaned_data['other_marketing_channel'],
                          marketing_channel=form.cleaned_data['marketing_channel'],
                          organization_website = form.cleaned_data['organization_website'],
                          timeline=form.cleaned_data['timeline'],
                          project_workflow=form.cleaned_data['project_workflow'],
                          dataset_availability=form.cleaned_data['dataset_availability'],
                          deliverable=form.cleaned_data['deliverable'],
                          skillset=skills_and_levels,
                          additional_skills=form.cleaned_data['additional_skills'],
                          technical_requirements=form.cleaned_data['technical_requirements'],
                          num_students=form.cleaned_data['num_students'],
                          other_num_students=form.cleaned_data['other_num_students'],
                          cloud_creds=form.cleaned_data['cloud_creds'],
                          meet_regularly=form.cleaned_data['meet_regularly'],
                          other_project_category=form.cleaned_data['other_project_category'],
                          hce_intern=form.cleaned_data['hce_intern'],
                          optional_q1=form.cleaned_data['optional_q1'],
                          optional_q2=form.cleaned_data['optional_q2'],
                          optional_q3=form.cleaned_data['optional_q3']
                          )
            proj.save()
            p = Partner.objects.filter(email_address = email)
            if len(p) > 0:
                p = Partner.objects.get(email_address = email)
            else:
                p = Partner(
                    email_address = email,
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                )
            p.save()
            p.projects.add(proj)
            link = PartnerProjectInfo(
                project = proj,
                partner = p,
                role = "Sponsor"
            )
            link.save()
            return redirect('/profile/')
        else:
            partner = Partner.objects.get(email_address = email)
            logger.error(f"Invalid form for partner {partner}:\n{form}")
            messages.info(
                request,
                'Your application was invalid and could not be processed. If this error persists, '
                'please contact ds-discovery@berkeley.edu.'
            )
            return redirect('/profile/')
    else:
        form = PartnerProjCreationForm()
        return render(request, 'projects/partner_proj_creation.html', {'form': form})

@login_required
def edit_project(request):
    email = None
    if request.user.is_authenticated:
        email = request.user.email
    proj_id = request.GET.get("project", -1)

    if proj_id != -1:
        project = Project.objects.get(id=proj_id)

        # Check project belongs to current user
        partner = Partner.objects.get(email_address=email)
        try:
            associated_partner = PartnerProjectInfo.objects.get(project=project, partner=partner)
        except PartnerProjectInfo.DoesNotExist:
                messages.info(request, 'Project not associated with the current user.')
                return redirect('/profile')


        if request.method == 'GET':
            project = Project.objects.get(id=proj_id)

            data = project.__dict__
            form = EditProjectForm(initial = data)

            # Different from Student.skill_levels_inverse -- E is capitalized in Experience here but not in the Student's dictionary. This is because project creation hardcoded this association. + add blank skill level option
            skill_levels_inverse = {
            'Familiar':'FA',
            'Beginner':'BE',
            'Intermediate':'IN',
            'Advanced':'AD',
            'No Experience':'NE',
            '':''
            }
            return render(request, 'projects/edit_project.html', {'form': form, 'project': project, 'skill_levels_inverse': skill_levels_inverse})

        elif request.method == 'POST':
            project = Project.objects.filter(id=proj_id)
            form = EditProjectForm(request.POST)
            if form.is_valid():
                skills_and_levels = {
                    "Python": form.cleaned_data["Python"],
                    "R": form.cleaned_data["R"],
                    "SQL": form.cleaned_data["SQL"],
                    "Tableau/Looker": form.cleaned_data["Tableau/Looker"],
                    "Data Visualization": form.cleaned_data["Data Visualization"],
                    "Data Manipulation": form.cleaned_data["Data Manipulation"],
                    "Text Analysis": form.cleaned_data["Text Analysis"],
                    "Machine Learning/Deep Learning": form.cleaned_data["Machine Learning/Deep Learning"],
                    "Geospatial Data, Tools and Libraries": form.cleaned_data["Geospatial Data, Tools and Libraries"],
                    "Web Development (frontend, backend, full stack)": form.cleaned_data["Web Development (frontend, backend, full stack)"],
                    "Mobile App Development": form.cleaned_data["Mobile App Development"],
                    "Cloud Computing": form.cleaned_data["Cloud Computing"],
                }
                for i in skills_and_levels.keys():
                    if skills_and_levels[i] == 'FA':
                        skills_and_levels[i] = 'Familiar'
                    elif skills_and_levels[i] == 'BE':
                        skills_and_levels[i] = 'Beginner'
                    elif skills_and_levels[i] == 'IN':
                        skills_and_levels[i] = 'Intermediate'
                    elif skills_and_levels[i] == 'AD':
                        skills_and_levels[i] = 'Advanced'
                    elif skills_and_levels[i] == 'NE':
                        skills_and_levels[i] = 'No Experience'
                    else:
                        continue
                project.update(email = form.cleaned_data['email'])
                project.update(organization=form.cleaned_data['organization'])
                project.update(project_name=form.cleaned_data['project_name'])
                project.update(project_category=form.cleaned_data['project_sector'])
                project.update(description=form.cleaned_data['description'])
                project.update(organization_description=form.cleaned_data['organization_description'])
                # project.update(other_marketing_channel=form.cleaned_data['other_marketing_channel'])
                # project.update(marketing_channel=form.cleaned_data['marketing_channel'])
                project.update(organization_website = form.cleaned_data['organization_website'])
                project.update(timeline=form.cleaned_data['timeline'])
                project.update(project_workflow=form.cleaned_data['project_workflow'])
                project.update(dataset_availability=form.cleaned_data['dataset_availability'])
                project.update(deliverable=form.cleaned_data['deliverable'])
                project.update(skillset=skills_and_levels)
                project.update(additional_skills=form.cleaned_data['additional_skills'])
                project.update(technical_requirements=form.cleaned_data['technical_requirements'])
                project.update(num_students=form.cleaned_data['num_students'])
                project.update(other_num_students=form.cleaned_data['other_num_students'])
                project.update(cloud_creds=form.cleaned_data['cloud_creds'])
                # project.update(meet_regularly=form.cleaned_data['meet_regularly'])
                project.update(other_project_category=form.cleaned_data['other_project_category'])
                project.update(hce_intern=form.cleaned_data['hce_intern'])
                project.update(optional_q1=form.cleaned_data['optional_q1'])
                project.update(optional_q2=form.cleaned_data['optional_q2'])
                project.update(optional_q3=form.cleaned_data['optional_q3'])

                return redirect('/profile')
    messages.info(request, 'Invalid project requested.')
    return redirect('/profile')
