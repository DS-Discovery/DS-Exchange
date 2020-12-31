from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('studentApplication', views.studentApplication, name='studentApplication'),
    path('partnerlisting', views.partnerlisting, name='partnerlisting'),
    path('<str:project_name>/app', views.app, name='app'),
    path('<str:project_name>', views.partnerProjectView, name='partnerProjectView'),
    # path('<str:project_name>/editquestions', views.editProjectQuestions, name='editProjectQuestions'),
    # path('<str:project_name>/editprofile', views.editProjectProfile, name='editProjectProfile'),


    # path('<int:question_id>/results/', views.results, name='results'),


    # path('specifics/<int:question_id>/', views.detail, name='detail'),
]
