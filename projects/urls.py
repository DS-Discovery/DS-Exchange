from django.urls import path

from . import views

urlpatterns = [
    path('', views.list_projects, name='index'),
    # path('partnerlisting', views.partnerlisting, name='partnerlisting'),
    path('<path:project_name>/apply', views.apply, name='apply'),
    path('newproject', views.proj_creation, name='new_project'),
    # path('json', views.projects_json, name='projects_json'),
    # path('<str:project_name>', views.partnerProjectView, name='partnerProjectView'),
]
