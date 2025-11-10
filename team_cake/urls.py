from django.urls import path
from . import views

app_name = "team_cake"
urlpatterns = [
    path('', views.index, name='index'),
    path('goods/', views.goods, name='goods'),
]