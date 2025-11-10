from django.urls import path
from . import views

app_name = "team_UD"
urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.members, name="members"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("memo/", views.memo_view, name="memo"),
]
