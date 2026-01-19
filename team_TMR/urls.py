from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ユーザー認証
    # Django標準のログイン・ログアウトビューを使用
    
    # 【修正】 next_page='roadmap_list' を追加
    # これにより、ログイン成功後に「roadmap_list」という名前のURL（ロードマップ一覧）へ移動します
    path('login/', auth_views.LoginView.as_view(
        template_name='teams/team_TMR/registration/login.html',
        next_page='roadmap_list' 
    ), name='login'),

    # 【修正】 next_page='login' を追加
    # これにより、ログアウト後に「login」という名前のURL（ログイン画面）へ戻ります
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    # カスタムサインアップビュー
    path('signup/', views.SignUpView.as_view(), name='signup'),

    # プロフィール
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # ロードマップ
    path('roadmaps/', views.RoadmapListView.as_view(), name='roadmap_list'),
    path('roadmaps/new/', views.RoadmapCreateView.as_view(), name='roadmap_create'),
    path('roadmaps/<int:pk>/edit/', views.RoadmapUpdateView.as_view(), name='roadmap_edit'),
    path('roadmaps/<int:pk>/delete/', views.RoadmapDeleteView.as_view(), name='roadmap_delete'),

    # ES
    path('es/', views.ESListView.as_view(), name='es_list'),
    path('es/new/', views.ESCreateView.as_view(), name='es_create'),
    path('es/<int:pk>/edit/', views.ESUpdateView.as_view(), name='es_edit'),
    path('es/<int:pk>/delete/', views.ESDeleteView.as_view(), name='es_delete'),

    # トップページ
    path('', views.RoadmapListView.as_view(), name='home'),
]