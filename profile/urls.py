from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('student/profile', views.studentProfileView, name='studentProfileView'),
    # path('partner/profile', views.partnerProfileView, name='partnerProfileView'),
    path('', views.get_profile, name='get_profile'),
    path('signup', views.student_signup, name='student_signup'),
    path('edit', views.edit_student_profile, name='edit_student_profile'),
    path('edit', views.partnerProfileEdit, name='partnerProfileEdit'),
    path('login', views.google_auth_redirect, name='google_auth_redirect'),
]
