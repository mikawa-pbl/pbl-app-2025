from django.urls import path
from . import views

app_name = "agileca"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('gikamap/', views.gikamap, name='gikamap'),
    path('gikamap/imc/', views.imc, name='imc'),
    path('gikamap/secretariat/', views.secretariat, name='secretariat'),
    path('gikamap/health/', views.health, name='health'),
    path('gikamap/welfare/', views.welfare, name='welfare'),
    path('gikamap/library/', views.library, name='library'),
    path('gikamap/classrooms/', views.classrooms, name='classrooms'),
    path('gikamap/search_by_buildings/', views.search_by_buildings, name='search_by_buildings'),
    path("gikamap2/", views.gikamap2, name="gikamap2"),
]
