from django.urls import path
from . import views

app_name = "team_UD"
urlpatterns = [
    path("", views.index, name="index"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("api/companies/", views.get_companies, name="get_companies"),
    path("api/memo/<int:year>/<int:month>/<int:day>/", views.get_memo_by_date, name="get_memo_by_date"),
    path("api/memo/save/", views.save_memo, name="save_memo"),
    path("api/memo/delete/<int:memo_id>/", views.delete_memo, name="delete_memo"),
    # 統計ページ
    path("statistics/", views.statistics_view, name="statistics"),
    path("api/statistics/", views.get_statistics, name="get_statistics"),
    # 質問対策ページ
    path("questions/", views.questions_view, name="questions"),
    path("api/questions/upcoming-companies/", views.get_upcoming_companies, name="get_upcoming_companies"),
    path("api/questions/company/<int:company_id>/", views.get_company_questions, name="get_company_questions"),
    path("api/questions/save/", views.save_question_answer, name="save_question_answer"),
    # アカウント関連
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
