from django.urls import path
from . import views

app_name = "team_scim"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('home/', views.home_view, name='home'),
    path('create_reservation/', views.create_reservation_view, name='create_reservation'),
]