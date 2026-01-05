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
    path('api/favorite_toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('api/save_file/', views.save_file, name='save_file'),
    path('api/file/list/', views.get_project_files, name='get_project_files'),
    path('api/file/content/', views.get_file_content, name='get_file_content'),
    path('api/file/create/', views.create_file, name='create_file'),
    path('api/file/delete/', views.delete_file, name='delete_file'),
    path('api/file/rename/', views.rename_file, name='rename_file'),
    path('api/file/upload/', views.upload_file, name='upload_file'),
    path('api/file/create_folder/', views.create_folder, name='create_folder'),
    path('api/file/rename_folder/', views.rename_folder, name='rename_folder'),
    path('api/project/rename/', views.rename_project, name='rename_project'),
    path('api/project/<int:project_id>/download/', views.download_project, name='download_project'),
    path('project/<int:project_id>/compile/', views.compile_project, name='compile_project'),
    path('main/url/', views.url, name='url'),

    # カスタム404エラーページ
    path('<path:unmatched_path>/', views.handle_404_not_found, name='app_404'),
]
