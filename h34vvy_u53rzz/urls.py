from django.urls import path
from . import views

app_name = "h34vvy_u53rzz"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]
