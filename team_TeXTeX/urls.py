from django.urls import path
from . import views

app_name = "team_TeXTeX"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('main/', views.main, name='main'),
    path('editer/', views.editer, name='editer'),
    path('main/<str:select>', views.main_select),
]