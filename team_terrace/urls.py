from django.urls import path
from . import views

app_name = "team_c"
urlpatterns = [
    path('', views.index, name='index'),
    path('items/', views.items, name='items'),
]