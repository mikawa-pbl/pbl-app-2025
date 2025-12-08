from django.urls import path
from . import views

app_name = "teachers"
urlpatterns = [
#    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('', views.paper_list, name='paper_list'),                  # 一覧
    path('<int:pk>/', views.paper_detail, name='paper_detail'),     # 詳細
    path('new/', views.paper_create, name='paper_create'),          # 登録
    path('search/', views.paper_search, name='paper_search'),   
]
