from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.studentProfileView, name='studentProfileView'),
    path('student_signup', views.student_signup, name='student_signup'),
    path('student_signup_edit', views.student_profile_edit, name='student_profile_edit'),
    


]
