from django.urls import path

from . import views

urlpatterns = [
    path('', views.list_student_applications, name='index'),
    path('status', views.update_application_status, name='update_application_status')
]