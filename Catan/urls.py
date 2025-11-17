from django.urls import path
from . import views

app_name = "Catan"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('shirushiru/', views.shirushiru, name='shirushiru'),
]