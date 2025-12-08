from django.urls import path
from . import views

app_name = "takenoko"
urlpatterns = [
    path('', views.main, name='main'),
    path('members/', views.members, name='members'),
    path('product_details/', views.product_details, name='product_details'),
]