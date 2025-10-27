"""
URL configuration for pbl_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('team_TMR/', include('team_TMR.urls')),
    path('graphics/', include('graphics.urls')),
    path('team_terrace/', include('team_terrace.urls')),
    path('team_TeXTeX/', include('team_TeXTeX.urls')),
    path('team_cake/', include('team_cake.urls')),
    path('team_shouronpou/', include('team_shouronpou.urls')),
    path('h34vvy_u53rzz/', include('h34vvy_u53rzz.urls')),
]
