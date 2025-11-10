from django.urls import path
from . import views

app_name = "team_northcliff"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]