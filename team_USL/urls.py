from django.urls import path
from . import views

app_name = "team_USL"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]
