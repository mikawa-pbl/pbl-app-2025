# shiokara/urls.py
from django.urls import path
from . import views

app_name = "shiokara"

urlpatterns = [
    # ログイン関連
    path("login/", views.login_menu, name="login"),          # ← メニュー
    path("login/form/", views.login_view, name="login_form"),   # ← ログイン画面
    path("register/", views.register_view, name="register"),     # ← 新規登録画面
    path("logout/", views.logout_view, name="logout"),
    path("mypage/", views.my_page, name="my_page"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("tutorial/seen/", views.tutorial_seen, name="tutorial_seen"),
    path("sitemap/", views.sitemap, name="sitemap"),
    path("feedback/", views.site_feedback, name="site_feedback"),

    # 既存
    path("", views.login_menu, name="index"),  # shiokaraのトップページをログイン・新規登録メニューに変更
    path("departments/", views.department_list, name="department_list"),
    path("search/", views.company_search, name="company_search"),
    path("company/<int:pk>/", views.company_detail, name="company_detail"),
    path("company/<int:pk>/favorite/", views.toggle_favorite, name="company_favorite"),
    path("company/<int:pk>/post/",
         views.company_experience_post,
         name="company_experience_post"),
]
