from django.contrib import admin
from django.urls import path
from team_USL.views import room_search_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('templates/teams/team_USL', room_search_view, name='room_search'),
]
