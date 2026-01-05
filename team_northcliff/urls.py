from django.urls import path
from . import views, api

app_name = "team_northcliff"
urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.members, name="members"),
    path("ui/<str:username>/", views.ui, name="ui"),
    path("map_ui/<str:username>/", views.map_ui, name="map_ui"),  # 追加: マップUI（ユーザー名付き）
    # API endpoints
    path("api/<str:username>/user-data/", api.user_data_view, name="api_user_data"),
    path("api/facilities/", api.facilities_view, name="api_facilities"),
    path("api/users/", api.users_list_view, name="api_users_list"),
    path("api/<str:username>/access-facility/", api.access_facility_view, name="api_access_facility"),
    path("api/<str:username>/create-post/", api.create_post_view, name="api_create_post"),
]
