from django.urls import path
from . import views

app_name = "nanakorobiyaoki"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('mypage/', views.mypage, name='mypage'),
    path('users/', views.users, name='users'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_register/confirm/<str:user_id>/', views.user_register_confirm, name='user_register_confirm'),
    
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('communities/', views.community_list, name='community_list'),
    path('communities/create/', views.community_create, name='community_create'),
    path('communities/<int:community_id>/', views.community_detail, name='community_detail'),
    path('communities/<int:community_id>/members/', views.community_members, name='community_members'),
    path('communities/<int:community_id>/join/', views.community_join, name='community_join'),
    path('communities/<int:community_id>/leave/', views.community_leave, name='community_leave'),
    path('communities/<int:community_id>/posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/create/', views.comment_create, name='comment_create'),
    
    path('messages/', views.message_inbox, name='message_inbox'),
    path('messages/<str:partner_user_id>/', views.chat_room, name='chat_room'),

    path('<str:user_id>/', views.user_profile, name='user_profile'),
    path('<str:user_id>/edit/', views.user_profile_edit, name='user_profile_edit'),
]

