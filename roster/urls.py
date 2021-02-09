from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name = 'index'),
    path('', views.display_student_team_roster, name='display_student_team_roster')
]