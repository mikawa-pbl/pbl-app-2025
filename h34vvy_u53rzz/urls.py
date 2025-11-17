from django.urls import path

from . import views

app_name = "h34vvy_u53rzz"
urlpatterns = [
    path("", views.index, name="index"),
    path("help/", views.help, name="help"),
    path("waiting/<int:entry_id>/", views.waiting_view, name="waiting"),
    path("timeline/", views.timeline_view, name="timeline"),
]
