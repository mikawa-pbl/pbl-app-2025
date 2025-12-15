from django.urls import path
from . import views

app_name = "team_giryulink"

urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.members, name="members"),
    path("product/add/", views.add_product, name="add_product"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("product/<int:pk>/delete/", views.delete_product, name="delete_product"),
]
