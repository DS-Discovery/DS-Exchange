from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list', views.list_project_applicants, name='list_project_applicants'),
]