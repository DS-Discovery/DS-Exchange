from django.urls import path

from . import views

urlpatterns = [
    path('', views.list_projects, name='index'),
    path('partnerlisting', views.partnerlisting, name='partnerlisting'),
    path('<str:project_name>/apply', views.apply, name='apply'),
    path('<str:project_name>', views.partnerProjectView, name='partnerProjectView'),
    path('json', views.projects_json, name='projects_json'),
]
