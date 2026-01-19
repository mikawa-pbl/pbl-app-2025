from django.urls import path
from . import views

app_name = "team_giryulink"

urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.members, name="members"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("my-products/", views.my_products, name="my_products"),
    path("product/add/", views.add_product, name="add_product"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("product/<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("product/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("product/<int:pk>/purchase/", views.purchase_product, name="purchase_product"),
    path("chat/", views.chat_list, name="chat_list"),
    path("chat/<int:room_id>/", views.chat_room, name="chat_room"),
    path("history/", views.history, name="history"),
    path("add-product/", views.add_product_page, name="add_product"),
    path("my-page/", views.my_page, name="my_page"),
]
