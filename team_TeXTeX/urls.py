from django.urls import path
from . import views
from .api.compile_latex import compile_latex

app_name = "team_TeXTeX"
urlpatterns = [
    # アプリケーションのルートURL
    path('', views.index, name='index'),

    # メインビュー
    path('members/', views.members, name='members'),
    path('main/', views.main, name='main'),
    path('get_data/', views.get_data_for_table, name='get_data'), # これを追加

    # URLビュー
    path('url/', views.url, name='url'),

    # エディタビュー
    path('editer/', views.editer, name='editer'),

    # 関数詳細ページ(動的生成)
    path('functions/<str:function_slug>/', views.function_template, name='function_template'),

    # APIエンドポイント
    path('api/compile/', compile_latex, name='api_compile_latex'),

    # カスタム404エラーページ
    path('<path:unmatched_path>/', views.handle_404_not_found, name='app_404'),
]
