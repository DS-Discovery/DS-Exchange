from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('studentApplication', views.studentApplication, name='studentApplication'),

    path('<str:project_name>/app', views.detail, name='detail'),
    # ex: /projects/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /projects/5/vote/

    path('specifics/<int:question_id>/', views.detail, name='detail'),
]
