from django.urls import path

app_name = 'students'
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
