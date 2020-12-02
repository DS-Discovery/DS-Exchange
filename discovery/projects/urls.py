from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('studentApplication', views.studentApplication, name='studentApplication'),

    path('<str:project_name>/app', views.app, name='app'),
    path('<str:project_name>', views.partnerProjectView, name='partnerProjectView'),


    path('<int:question_id>/results/', views.results, name='results'),


    path('specifics/<int:question_id>/', views.detail, name='detail'),
]
