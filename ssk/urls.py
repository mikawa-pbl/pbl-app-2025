from django.urls import path
from . import views

app_name = "ssk"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]