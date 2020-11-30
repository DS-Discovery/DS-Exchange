from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path("getNumApps/", views.getNumApps)
]