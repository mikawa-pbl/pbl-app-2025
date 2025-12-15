# team_kitajaki/urls.py

from django.urls import path
from . import views

app_name = "team_kitajaki"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('today-menu/', views.today_menu, name='today_menu'),
    path('today-menu/rate/', views.rate_menu, name='rate_menu'),
    
    # ★ 追加: ランキングページのURL
    path('menu_ranking/', views.menu_ranking, name='menu_ranking'),
]