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
from flags.state import flag_enabled

from applications.forms import AnswerForm
from applications.models import Answer, Application
from students.models import Student

from .forms import EditProjectForm
from .models import Partner, PartnerProjectInfo, Project, Question
from django.http import HttpResponse

logger = logging.getLogger(__name__)


# @login_required
def list_projects(request):
    # email = None
    # if request.user.is_authenticated:
    #     email = request.user.email

    # if email is None:
    #     return redirect('/profile/login')

    projects_json = get_projects_json()
    for i, project in list(enumerate(projects_json['projects']))[::-1]:
        if Application.objects.filter(project_id=project['id']).count() >= config.HIDE_PROJECT_APPLICATION_THRESHOLD:
            projects_json['projects'].pop(i)

    return render(request, 'projects/listing.html', {"projects_json": projects_json})


def get_projects_json():
    projects = []
    for p in Project.objects.all():
        d = p.to_dict()
        if d['archived'] != "Yes":
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
        questions = Question.objects.filter(project = project)#.order_by('question_num')
    except Question.DoesNotExist:
        raise Http404("Question does not exist.")

    email = None
    if request.user.is_authenticated:
        email = request.user.email
    else:
        messages.info("You must be logged in to apply to a project.")
        return redirect('/')
    
    try:
        student = Student.objects.get(email_address = email)
    except ObjectDoesNotExist:
        if Partner.objects.filter(email_address = email).count() > 0:
            messages.info(request, "You must be a student to apply to projects.")
            return redirect("/projects")
        else:
            messages.info(request, "You have not yet signed up. Please complete the signup form to continue.")
            return redirect("/profile/signup")

    if not flag_enabled('APPLICATIONS_OPEN'):
        messages.info(
            request, 
            "Applications are currently closed. If you believe you have received "
            "this message in error, please email ds-discovery@berkeley.edu."
        )
        return redirect("/projects")

    count = Application.objects.filter(student = student).count()

    if count > config.APP_LIMIT - 1 and not student.is_scholar:
        messages.info(request, f'You have already applied to {config.APP_LIMIT} projects.')
        return redirect('/projects')
    elif count > config.SCHOLAR_APP_LIMIT - 1 and student.is_scholar:
        messages.info(request, f'You have already applied to {config.SCHOLAR_APP_LIMIT} projects.')
        return redirect('/projects')

    count = Application.objects.filter(student = student, project = project).count()

    if count > 0:
        # raise Http404("Student already has an application submitted")
        messages.info(request, 'You have already applied to this project.')
        return redirect('/projects')

    #if this form is submitted, then we want to save the answers
    if request.method == 'POST':

        post = request.POST.copy()
        # print(post)

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

        if is_valid:

            try:
                application = Application.objects.get(student=student, project=project)
            except:
                 application = Application(student=student, project=project, status = "SUB")

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
                        a = Answer(
                            student=student, application = application, question = question, 
                            answer_text = form.cleaned_data['answer_text']
                        )
                    
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
        return render(request, 'projects/application.html', {'questions': questions, 'project' : project, 'form' : form})
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

