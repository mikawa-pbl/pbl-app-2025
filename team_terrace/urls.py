from django.urls import path

from . import api_views, views

app_name = "team_terrace"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("room/<uuid:room_id>/", views.RoomView.as_view(), name="room"),
    path("api/room/<uuid:room_id>/messages/", api_views.PostMessageView.as_view(), name="post_message"),
    path("api/room/<uuid:room_id>/messages/list/", api_views.GetMessagesView.as_view(), name="get_messages"),
    path("api/messages/<int:message_id>/replies/", api_views.PostReplyView.as_view(), name="post_reply"),
    path("api/messages/<int:message_id>/replies/list/", api_views.GetRepliesView.as_view(), name="get_replies"),
    path("api/room/<uuid:room_id>/reactions/", api_views.PostReactionView.as_view(), name="post_reaction"),
    path("api/room/<uuid:room_id>/reactions/list/", api_views.GetReactionsView.as_view(), name="get_reactions"),
    path("api/messages/<int:message_id>/like/", api_views.PostLikeView.as_view(), name="post_like"),
    path("api/messages/<int:message_id>/unlike/", api_views.PostUnlikeView.as_view(), name="post_unlike"),
    path("api/room/<uuid:room_id>/likes/", api_views.GetLikesView.as_view(), name="get_likes"),
]
