# team_kitajaki/urls.py

from django.urls import path
from . import views

app_name = "team_kitajaki"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('today-menu/', views.today_menu, name='today_menu'),  # ← ここだけでOK
]
