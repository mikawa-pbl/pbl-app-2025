from django.urls import path
from . import views

app_name = "ssk"
urlpatterns = [
    # 掲示板
    path('', views.post_list, name='post_list'),
    path('new/', views.post_create, name='post_create'),
]
