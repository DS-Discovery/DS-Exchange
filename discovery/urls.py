"""discovery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.conf.urls import handler403, handler404
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from .views import status_400, status_403, status_404, status_500

urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('applications/', include('applications.urls')),
    path('profile/', include('user_profile.urls')),
    path('projects/', include('projects.urls')),
<<<<<<< HEAD
    path('resources/', include('resources.urls')),
=======
    path('roster/', include('roster.urls')),
>>>>>>> 345567349264a33291e4ef1c82ddff32e9f158e6
]

handler400 = status_400 #'discovery.views.status_403'
handler403 = status_403 #'discovery.views.status_403'
handler404 = status_404 # 'discovery.views.status_404'
handler500 = status_500
