from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, Http404, render, redirect
from django.template.context_processors import csrf

from applications.forms import AnswerForm
from applications.models import Answer, Application
from students.models import Student

from .forms import EditProjectForm
from .models import Partner, PartnerProjectInfo, Project, Question


@login_required
def list_projects(request):
    # for category dropdown

    email = None
    if request.user.is_authenticated:
        email = request.user.email
    # student_exists = Student.objects.filter(email_address = email).exists()

    if email is None:
        return redirect('/profile/login')

    # project_category_list = set()
    # for e in Project.objects.all():
    #     categories = e.project_category.strip().split(';')
    #     categories = [cat.strip() for cat in categories]
    #     project_category_list.update(categories)

    # project_category_list = sorted(list(project_category_list))
    # latest_question_list = Project.objects.order_by('project_name')
    # context = {
    #     'latest_question_list': latest_question_list,
    #     'project_category_list': project_category_list,
    # }

    # # need to send requested category back to keep category selected
    # if request.GET.get('category_wanted') or request.GET.get('project_wanted'):
        
    #     # here when select dropdown category
    #     category = request.GET.get('category_wanted')
    #     project = request.GET.get('project_wanted')

    #     if category:
    #         # send selected category back
    #         context["selected_category"] = category
    #         latest_question_list = Project.objects.filter(project_category__contains=category)
    #         context["latest_question_list"] = latest_question_list

    #     if project:
    #         context["selected_project"] = Project.objects.filter(project_name=project)[0]
            
    #         selected_partner = None
    #         for partner in Partner.objects.all():
    #             projects = [p.project for p in partner.partnerprojectinfo_set.all()]
    #             if context["selected_project"] in projects:
    #                 selected_partner = partner
            
    #         context["selected_partner"] = selected_partner
    #         context["labels"] = context["selected_project"].project_category.split(";")

    #         context["num_applicants"] = len(Application.objects.filter(project=context["selected_project"]))

    return render(request, 'projects/listing.html', {"projects_json": get_projects_json()})


def get_projects_json():
    projects = []
    for p in Project.objects.all():
        d = p.to_dict()
        d["num_applicants"] = Application.objects.filter(project=p).count()
        projects.append(d)

    projects = sorted(projects, key=lambda d: d["project_name"])

    return {"projects": projects}


# def detail(request, project_name):
#     try:
#         project = Project.objects.get(project_name=project_name)
#         print(project, project_name)
#         # print([e.project_name for e in Partner.objects.all()])
#         questions = Question.objects.filter(project = project)
#         # questions = question.objects.get(project_name = project)

#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'project.html', {'project': project})


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

    count = Application.objects.filter(student = student).count()

    if count > 2:
        messages.info(request, 'You have already applied to 3 projects.')
        return redirect('/projects')

    count = Application.objects.filter(student = student, project = project).count()

    if count > 0:
        # raise Http404("Student already has an application submitted")
        messages.info(request, 'You have already applied to this project.')
        return redirect('/projects')

    #if this form is submitted, then we want to save the answers
    if request.method == 'POST':

        post = request.POST.copy()
        print(post)

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

        print(ans_list)

        if is_valid:

            try:
                application = Application.objects.get(student=student, project=project)
            except:
                 application = Application(student=student, project=project, status = "SUB")

            application.save()

            for post in ans_list:
                print(post)

                request.POST = post

                form = AnswerForm(request.POST)

                if form.is_valid():
                    print("Is valid")
                    
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

                else:
                    print("not valid")
                    print(form.errors)

            # TODO: allow students to update rank
            studentUpdater = Student.objects.filter(email_address = email)
            if not student.first_choice:
                studentUpdater.update(first_choice = project.project_name)
            elif not student.second_choice:
                studentUpdater.update(second_choice = project.project_name)
            elif not student.third_choice:
                studentUpdater.update(third_choice = project.project_name)
            # else:
            #     # raise Http404("Student has applied to 3 applications")
            #     messages.info(request, 'You have already applied to 3 projects.')
            #     return redirect('/projects')

            messages.info(request, 'Your application has been submitted successfully!')
            return redirect('/projects')
        
        else:
            messages.info(
                request, 
                'Your application was invalid and could not be processed. If this error persists, '
                'please contact <a href="mailto:ds-discovery@berkeley.edu">ds-discovery@berkeley.edu</a>.'
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


# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)

# @login_required
# def partnerProjectView(request, project_name):
#     email = None
#     if request.user.is_authenticated:
#         email = request.user.email

#     try:
#         context = Partner.objects.get(email_address = email)
#     except ObjectDoesNotExist:
#         return HttpResponseForbidden("User is not a partner.")
#     # projects = context.projects.all()
#     # breakpoint()
#     canView = False
#     for ppi in context.partnerprojectinfo_set.all():
#         project = ppi.project
#         if project.project_name == project_name:
#             canView = True
#     if not canView:
#         return HttpResponseForbidden("User lacks permission to view this project.")
#     project = Project.objects.get(project_name=project_name)
#     questions = Question.objects.filter(project = project).order_by('question_num')


#     projectPartnerRoles = PartnerProjectInfo.objects.filter(project = project)

#     return render(request, 'projects/partnerProjectView.html', {'questions': questions, 'project' : project, 'projectPartnerRoles': projectPartnerRoles})


# @login_required
# def partnerlisting(request):
#     # for category dropdown
#     email = None
#     if request.user.is_authenticated:
#         email = request.user.email
#     context = Partner.objects.get(email_address = email)
#     roles = PartnerProjectInfo.objects.filter(partner = context)
#     projects = [p.project for p in roles]

#     # project_category_list = set()
#     # for e in projects:
#     #     categories = e.project_category.strip().split(',')
#     #     categories = [cat.strip() for cat in categories]
#     #     project_category_list.update(categories)
#     # project_category_list = sorted(list(project_category_list))


#     latest_question_list = projects
#     context = {'latest_question_list': latest_question_list}

#     # need to send requested category back to keep category selected
#     if request.method == "POST":
#         # here when select dropdown category
        
#         project = request.POST.get('project_wanted')
#         print("project_wanted is", project)
       
#         if project:
#             project = project.split("+")[0]
            

      
#         if project:
#             context["selected_project"] = Project.objects.filter(project_name=project)[0]
#             # selected_partner = None
#             # for partner in Partner.objects.all():
#             #     projects = partner.projects.all()
#             #     if context["selected_project"] in projects:
#             #         selected_partner = partner
#             # context["selected_partner"] = selected_partner
#             context["labels"] = context["selected_project"].project_category.split(";")
#             context['partnerProjectInfos'] = PartnerProjectInfo.objects.filter(project = context["selected_project"])
     
#             questions = Question.objects.filter(project = context["selected_project"]).order_by('question_num')
#             context['questions'] = questions
#             context["count"] = len(Application.objects.filter(project =  context["selected_project"]))

#     # print("context", context)
#     # print("latest_question_list", latest_question_list)
    
#     return render(request, 'projects/partnerListing.html', context)
