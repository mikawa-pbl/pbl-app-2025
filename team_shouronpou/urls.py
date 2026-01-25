from django.urls import path
from . import views

app_name = "team_shouronpou"

urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('board/', views.PostListView.as_view(), name='post_list'),
    path('board/new/', views.PostCreateView.as_view(), name='post_new'),
    path('board/post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('board/post/<int:pk>/apply/', views.apply_for_post, name='post_apply'),
    path('board/post/<int:pk>/cancel/', views.cancel_application, name='cancel_application'), # 追加
    path('board/post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('board/post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/edit/', views.profile_edit, name='profile_edit'),
]