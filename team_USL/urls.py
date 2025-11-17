from django.urls import path
from . import views

app_name = "team_USL"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('images/<path:filename>', views.serve_template_image, name='usl_image'),
]
