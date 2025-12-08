from django.contrib import admin
from django.urls import path
from team_USL.views import room_search_view

urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('images/<path:filename>', views.serve_template_image, name='usl_image'),
]
