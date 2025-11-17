from django.urls import path
from . import views

app_name = "mori_doragon_yuhi_machi"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]