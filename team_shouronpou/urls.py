from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = "team_shouronpou"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    # --- ここから掲示板機能のURL ---
    
    # 投稿一覧 (例: /team_shouronpou/board/)
    path('board/', views.PostListView.as_view(), name='post_list'),
    
    # 新規投稿 (例: /team_shouronpou/board/new/)
    path('board/new/', views.PostCreateView.as_view(), name='post_new'),
    
    # 投稿詳細 (例: /team_shouronpou/board/post/1/)
    path('board/post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),

    # 募集人数
    path('board/post/<int:pk>/apply/', views.apply_for_post, name='post_apply'),
    
    # 投稿編集 (例: /team_shouronpou/board/post/1/edit/)
    path('board/post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    
    # 投稿削除 (例: /team_shouronpou/board/post/1/delete/)
    path('board/post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # ログインなど
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/edit/', views.profile_edit, name='profile_edit'),
]
