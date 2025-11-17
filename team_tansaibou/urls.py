from django.urls import path

from . import views

app_name = "team_tansaibou"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('register-sale/', views.register_sale, name='register_sale'),
    path('sales/', views.sale_list, name='sale_list'),
]