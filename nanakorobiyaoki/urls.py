from django.urls import path
from . import views

app_name = "nanakorobiyaoki"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('mypage/', views.mypage, name='mypage'),
    path('users/', views.users, name='users'),
    path('<str:user_id>/', views.user_profile, name='user_profile'),
]