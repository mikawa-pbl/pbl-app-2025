# papers/urls.py
from django.urls import path
from . import views

app_name = 'teachers'   # 名前空間を付ける（テンプレートで papers:paper_detail などと書く）

urlpatterns = [
    path('', views.paper_list, name='paper_list'),
    path('search/', views.paper_search, name='paper_search'),
    path('new/', views.paper_create, name='paper_create'),
    path('<int:pk>/', views.paper_detail, name='paper_detail'),
    path('<int:pk>/edit/', views.paper_update, name='paper_update'),
    path('<int:pk>/delete/', views.paper_delete, name='paper_delete'),
]
