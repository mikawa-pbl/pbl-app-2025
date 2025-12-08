from django.urls import path

from . import views

app_name = "h34vvy_u53rzz"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("help/", views.help, name="help"),
    path("waiting/<int:entry_id>/", views.waiting_view, name="waiting"),
    path(
        "waiting/<int:entry_id>/status/",
        views.waiting_status,
        name="waiting_status",
    ),
    path("timeline/", views.timeline_view, name="timeline"),
]
