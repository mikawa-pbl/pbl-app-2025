from django.urls import path
from . import views

app_name = "team_cake"
urlpatterns = [
    path('', views.index, name='index'),
    # path('goods/', views.goods, name='goods'),
    path('registration_goods/', views.registration_goods, name='registration_goods'),
    path('delete_good/<str:pk>/', views.delete_good, name='delete_good'),
    path('images/<path:filename>', views.serve_template_image, name='cake_image'),
]