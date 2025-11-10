from django.urls import path
from . import views

app_name = "team_UD"
urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.members, name="members"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("memo/", views.memo_view, name="memo"),
    path("api/memo/<int:year>/<int:month>/<int:day>/", views.get_memo_by_date, name="get_memo_by_date"),
    path("api/memo/save/", views.save_memo, name="save_memo"),
    path("api/memo/delete/<int:memo_id>/", views.delete_memo, name="delete_memo"),
]
