from django.urls import path
from . import views

""" 画面遷移図（UI フロー）
[トップページ (掲示板一覧)]
    │
    ├── [検索・フィルタリング] ──> [一覧更新]
    │
    ├── [詳細ページ]
    │       │
    │       ├── [応募するボタン] ──(別タブ)──> [Google Forms]
    │       │
    │       ├── [編集ボタン] ──> [パスワード入力画面] ──(一致)──> [編集画面] ──(保存)─
    │       │
    │       └── [削除ボタン] ──> [パスワード入力画面] ──(一致)──> [削除実行] ──> [トッ
    │
    └── [新規投稿ボタン]
            │
            └── [新規投稿画面]
                    ├── [主催者名入力]
                    ├── [パスワード設定 (4桁数字)] (必須)
                    ├── [Google Forms URL] (必須)
                    ├── [テンプレート適用ボタン]
                    └── (投稿する) ──> [トップページへ]
"""

urlpatterns = [
    # 掲示板一覧 (トップページ)
    path('', views.ExperimentListView.as_view(), name='experiment_list'),
    
    # 詳細ページ
    path('post/<int:pk>/', views.ExperimentDetailView.as_view(), name='experiment_detail'),
    
    # 新規投稿
    path('post/new/', views.ExperimentCreateView.as_view(), name='experiment_create'),
    
    # パスワード確認 (action: edit または delete)
    path('post/<int:pk>/password/<str:action>/', views.PasswordConfirmView.as_view(), name='password_confirm'),
    
    # 編集
    path('post/<int:pk>/edit/', views.ExperimentUpdateView.as_view(), name='experiment_edit'),
    
    # 削除
    path('post/<int:pk>/delete/', views.ExperimentDeleteView.as_view(), name='experiment_delete'),
]