from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('student/profile', views.studentProfileView, name='studentProfileView'),
    path('partner/profile', views.partnerProfileView, name='partnerProfileView'),
    path('profile/', views.redirectProfile, name='redirectProfile'),
    
    path('student/signup', views.studentSignup, name='studentSignup'),
    path('student/edit', views.studentProfileEdit, name='partnerProfileEdit'),
    path('partner/edit', views.partnerProfileEdit, name='partnerProfileEdit'),
        


]
