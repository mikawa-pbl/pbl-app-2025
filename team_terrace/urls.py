from django.urls import path
from . import views

app_name = "team_terrace"
urlpatterns = [
    path("", views.index, name="index"),
    path("room/<uuid:room_id>/", views.room, name="room"),
    path("api/room/<uuid:room_id>/messages/", views.post_message, name="post_message"),
    path("api/room/<uuid:room_id>/messages/list/", views.get_messages, name="get_messages"),
]
