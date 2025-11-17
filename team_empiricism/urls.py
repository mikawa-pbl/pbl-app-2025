from django.urls import path
from . import views
from .views import BoardView # BoardView をインポート

app_name = "team_empiricism" # 変更
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    # --- ここから掲示板用のパスを追加 ---
    # (例: /team_empiricism/board/ というURLでアクセス)
    path('board/', BoardView.as_view(), name='board'),
    # --- ここまで追加 ---
]